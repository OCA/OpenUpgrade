<?php

# Needed to fix a bug in ZF 1.5.1
# http://framework.zend.com/issues/browse/ZF-2978
class My_XmlRpc_Client extends Zend_XmlRpc_Client
{
    public function call($method, $params = array())
    {
        $request = new Zend_XmlRpc_Request($method, $params);

        $this->doRequest($request);

        if ( $this->getLastResponse()->isFault() ) 
		{
            $fault = $this->getLastResponse()->getFault();
            throw new Zend_XmlRpc_Client_FaultException($fault->getMessage(),
                                                        $fault->getCode());
        }

        return $this->getLastResponse()->getReturnValue();
    }
}

class Smile_OpenERPSync_Model_Observer
    extends Mage_Core_Model_Abstract 
{
	/**
	* Export an order on completion
	*
	* @triggeredby: checkout_type_onepage_save_order_after 
	*               (when sales_order_place_after fires the order doesn't have an id yet)
	* @param $eventArgs array "order"=>$order
	*/
	public function exportOnOrderEvent($observer) 
	{
		if (Mage::getStoreConfig('openerpsync/settings/enabled'))
		{
			$order = $observer->getEvent()->getOrder();
			$saleOrder = $this->get_sale_order($order);
			$this->createOrder($saleOrder);
		}
		return $this;
	}

	
	function debugEnabled()
	{
		return Mage::getStoreConfig('openerpsync/settings/debug_flag');
	}
	
	function getServerURL()
	{
		$server =   Mage::getStoreConfig('openerpsync/settings/server_url');
		
		# make sure the server url ends with a /
		if ( substr($server, -1) != "/" )
		{
			$server .= "/";
		}
		
		return $server;
	}

	/**
	* calls OpenERP to place the order
	* @param array XML/RPC hash of the Magento sale order
	* @return bool true if the order was created
	*/
	function createOrder($saleOrder)
	{
		if ( $this->debugEnabled() )
		{
			Mage::Log($saleOrder);
		}
		
		try 
		{
			$server = $this->getServerURL();
			$database = Mage::getStoreConfig('openerpsync/settings/database');
			$userName = Mage::getStoreConfig('openerpsync/settings/api_username');
			$password = Mage::getStoreConfig('openerpsync/settings/api_password');
			
			if ( $this->debugEnabled() )
			{
				Mage::Log("Server: " . $server);
				Mage::Log("Database: " . $database);
				Mage::Log("UserName: " . $userName);
				Mage::Log("Password: " . $password);
			}
			
			# login to get user id
			$conn = new My_XmlRpc_Client($server . "common");
			$client = $conn->getProxy();
			$userId = $client->login($database, $userName, $password);
			
			# create the order in OpenERP
			$conn = new My_XmlRpc_Client($server . "object");
			$client = $conn->getProxy();
			$result = $client->execute($database, $userId, $password, "magento.web", "createOrders", array($saleOrder));

			if ( $this->debugEnabled() )
			{
				Mage::Log("Request: " . $conn->getLastRequest()->__toString());
				Mage::Log("Response: " . $conn->getLastResponse()->__toString());
			}
		
			if ($result['has_error'] > 0 )
			{
				return false;
			}
		} 
		catch (Zend_XmlRpc_Exception $e ) 
		{
			Mage::Log("My_XmlRpc_Client execute Failed: " . $e->getMessage());
			Mage::getSingleton('checkout/session')->addError($e->getMessage());
			return false;
		}
		catch (Mage_Core_Exception $e) 
		{
			Mage::Log("Core Exception: " . $e->getMessage());
			Mage::getSingleton('checkout/session')->addError($e->getMessage());
			return false;
		}
		catch (Exception $e) 
		{
			Mage::Log("Exception: " . $e->getMessage());
			Mage::getSingleton('checkout/session')->addException(
				$e,
				Mage::helper('checkout')->__('OpenERP Sync Error')
			);
			return false;
		}
		
		return true;
	}

	/** Grab the Magento sale order with the requested id
	* @param int sale_order_id int: Magento sale order id
	* @return array XML/RPC hash of the Magento sale order
	*/
	function get_sale_order($order) 
	{               
		$productArray=array();  // sale order line product wrapper

		// Magento required models
		$customer = Mage::getModel('customer/customer')->load($order->getCustomerId());
		
		// walk the sale order lines
		foreach ($order->getAllItems() as $item) 
		{
			$productArray[] = array(
				"product_sku" => $item->getSku(),
				"product_magento_id" => $item->getProductId(),
				"product_name" => $item->getName(),
				"product_qty" => $item->getQtyOrdered(),
				"product_price" => $item->getPrice(),
				"product_discount_amount" => $item->getDiscountAmount(),
				"product_row_price" => $item->getPrice() - $item->getDiscountAmount(),
			);
		}
		
		$streetBA=$order->getBillingAddress()->getStreet();
		$streetSA=$order->getShippingAddress()->getStreet();

		$saleorder =  array(
			"id" => $order->getId(),
			"store_id" => $order->getStoreId(),
			"payment"=> $order->getPayment()->getMethod(),
			"shipping_amount" => $order->getShippingAmount(),
			"grand_total" => $order->getGrandTotal(),
			"date"=> $order->getCreatedAt(),
			"lines" => $productArray,
			"shipping_address" =>    array(
				"firstname"=> $order->getShippingAddress()->getFirstname(),
				"lastname"=> $order->getShippingAddress()->getLastname(),
				"company"=> $order->getShippingAddress()->getCompany(),
				"street" => $streetSA[0],
				"street2" => (count($streetSA)==2)?$streetSA[1]:'',
				"city"=> $order->getShippingAddress()->getCity(),
				"postcode"=> $order->getShippingAddress()->getPostcode(),
				"country"=> $order->getShippingAddress()->getCountry(),
				"phone"=> $order->getShippingAddress()->getTelephone()
			),
			"billing_address" =>     array(
				"firstname"=> $order->getBillingAddress()->getFirstname(),
				"lastname"=> $order->getBillingAddress()->getLastname(),
				"company"=> $order->getBillingAddress()->getCompany(),
				"street" => $streetBA[0],
				"street2" => (count($streetBA)==2)?$streetBA[1]:'',
				"city"=> $order->getBillingAddress()->getCity(),
				"postcode"=> $order->getBillingAddress()->getPostcode(),
				"country"=> $order->getBillingAddress()->getCountry(),
				"phone"=> $order->getBillingAddress()->getTelephone()
			),
			"customer" => array(
				"customer_id"=> $customer->getId(),
				"customer_name"=> $customer->getName(),
				"customer_email"=> $customer->getEmail()
			),
				
		);
		
		return $saleorder;
	}
}
?>
