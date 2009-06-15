<?php

/**
 * @author Raphaël Valyi, Sylvain Pamart
 * @copyright 2008-2009
 */

class Smile_OpenERPSync_Model_Order_Api extends Mage_Sales_Model_Order_Api
{


	function __order2array($order) {
		$customer = Mage::getModel('customer/customer')->load($order->getCustomerId());

		// walk the sale order lines
		$productArray=array();	// sale order line product wrapper
		foreach ($order->getAllItems() as $item) {
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
	
		return array(
			"id" => $order->getId(),
			"store_id" => $order->getStoreId(),
			"payment"=> $order->getPayment()->getMethod(),
			"shipping_amount" => $order->getShippingAmount(),
			"grand_total" => $order->getGrandTotal(),
			"date"=> $order->getCreatedAt(),
			"lines" => $productArray,
			"shipping_address" =>	 array(
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
			"billing_address" =>	 array(
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
	}

	
	function infoAll($saleOrderId = null) {
		$order = Mage::getModel('sales/order')->load($saleOrderId);//TODO deal with order not found
		return $this->__order2array($order);
	}


	public function update($saleOrder = null)
	{
		$saleOrder = $saleOrder[0];
		$order = Mage::getModel('sales/order')->load($saleOrder['magento_id']);//TODO deal with order not found
		
		//	status matching TODO can't do better?
		if($saleOrder['status'] == ''){$order->setStatus(Mage_Sales_Model_Order::STATE_NEW, true);}
		if($saleOrder['status'] == 'progress'){$order->setStatus(Mage_Sales_Model_Order::STATE_PROCESSING, true);}
		if($saleOrder['status'] == 'shipping_except'){$order->setStatus(Mage_Sales_Model_Order::STATE_COMPLETE, true);}
		if($saleOrder['status'] == 'invoice_except'){$order->setStatus(Mage_Sales_Model_Order::STATE_COMPLETE, true);}
		if($saleOrder['status'] == 'done'){$order->setStatus(Mage_Sales_Model_Order::STATE_CLOSED, true);}
		if($saleOrder['status'] == 'cancel'){$order->setStatus(Mage_Sales_Model_Order::STATE_CANCELED, true);}
		if($saleOrder['status'] == 'waiting_date'){$order->setStatus(Mage_Sales_Model_Order::STATE_HOLDED, true);}
		
		$order->save();
		return $order->getId();
		$stores = array();
		return $stores;
	}
	
	
	/**
	* @param int last_sale_order_id
	* @return array saleorders
	* TODO use a isExported flag instead, that would be way more reliable, especially during on the live exports but for that we need to add that custom flag to Magento sale orders!
	*/
	function listNew($lastSaleOrderId) {
		$saleorders=array();  

		//	retrieve the next sale orders
		$order_collection = Mage::getResourceModel('sales/order_collection')
			->addAttributeToSelect('entity_id')
			->addAttributeToSort('entity_id', 'desc')
			->load();
			
		$max_order_id=$order_collection->getFirstItem()->getId();
		
		/* iterate over the sale orders */
		for ($id = $lastSaleOrderId+1; $id <= $max_order_id; $id++) {
			$order = Mage::getModel('sales/order')->load($id);
			$saleorders[] =  $this->__order2array($order);
		}
		
		return $saleorders;
	}
	
	
}

?>
