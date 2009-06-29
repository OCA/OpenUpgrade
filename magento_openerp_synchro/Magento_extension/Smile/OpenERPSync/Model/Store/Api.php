<?php

/**
 * @author 
 * @copyright 2008
 */

class Smile_OpenERPSync_Model_Store_Api extends Mage_Catalog_Model_Api_Resource
{
	/*
	<param><value><string>92mliq7v01g1k9ofv14v8d0gd2</string></value></param>
	<param><value><string>catalog_store.websites</string></value></param>
	optional: <param><value><array><data><value><i4>0</i4></value></data></array></value></param>
	*/
	public function websites($websiteId = null)
	{
		$websites = array();
		
		if(is_integer($websiteId))
		{
			try{
				return $this->_websiteToArray(Mage::app()->getWebsite($websiteId));
			} catch (Mage_Core_Exception $e) {
                $this->_fault('website_not_exists');
            }
		} else {
			foreach(Mage::app()->getWebsites(true) as $websiteId => $website)
			{
				$websites[] = $this->_websiteToArray($website);
			}
			
			return $websites;
		}
	}
	
	protected function _websiteToArray($website)
	{
		return array(	'website_id' 		=> $website->getWebsiteId(),
						'code'				=> $website->getCode(),		
						'name'				=> $website->getName(),		
						'sort_order'		=> $website->getSortOrder(),
						'default_group_id'	=> $website->getDefaultGroupId(),
						'is_default'		=> $website->getIsDefault(),
						'group_ids'			=> $website->getGroupIds()
						);
	}
	
	/*
	<param><value><string>92mliq7v01g1k9ofv14v8d0gd2</string></value></param>
	<param><value><string>catalog_store.stores</string></value></param>
	*/
	public function stores($storeIds = null)
	{
		$stores = array();
		
		if(is_array($storeIds))
		{
			foreach($storeIds as $storeId)
			{
				try{
					$stores[] = $this->_storeToArray(Mage::app()->getStore($storeId));
				} catch (Mage_Core_Exception $e) {
	                $this->_fault('store_not_exists');
	            }
			}
			
			return $stores;
		} 
		elseif(is_numeric($storeIds))
		{
			try{
				return $this->_storeToArray(Mage::app()->getStore((int)$storeIds));
			} catch (Mage_Core_Exception $e) {
                $this->_fault('store_not_exists');
            }
		} else {
			foreach(Mage::app()->getStores(true) as $storeId => $store)
			{
				$stores[] = $this->_storeToArray($store);
			}
			
			return $stores;	
		}
	}
	
	protected function _storeToArray($store)
	{
		return array(	'store_id' 					=> $store->getStoreId(),
						'code'						=> $store->getCode(),
						'website_id'				=> $store->getWebsiteId(),
						'group_id'					=> $store->getGroupId(),
						'name'						=> $store->getName(),
						'sort_order'				=> $store->getSortOrder(),
						'is_active'					=> $store->getIsActive(),
						'is_admin'					=> $store->isAdmin(),
						'is_can_delete'				=> $store->isCanDelete(),
						'url'						=> $store->getUrl(),
						'is_currently_secure' 		=> $store->isCurrentlySecure(),
						'current_currency_code' 	=> $store->getCurrentCurrencyCode(),
						'root_category_id'			=> $store->getRootCategoryId()
						);	
	}
	
	public function groups($groupIds)
	{
		if(is_array($groupIds))
		{
			$groups = array();
			foreach($groupIds as $groupId)
			{
				$groups[] = $this->_groupToArray($groupId);
			}
			return $groups;
		} 
		elseif(is_integer($groupIds))
		{
			return $this->_groupToArray($groupIds);	
		} else {
			$this->_fault('group_not_exists');	
		}
	}
	
	protected function _groupToArray($groupId)
	{
		try
		{
			$group = Mage::app()->getGroup($groupId);
		
			return array(	'group_id'			=> $group->getGroupId(),
							'website_id'		=> $group->getWebsiteId(),
							'name'				=> $group->getName(),
							'root_category_id'	=> $group->getRootCategoryId(),
							'default_store_id'	=> $group->getDefaultStoreId(),
							'store_ids'			=> $group->getStoreIds(),
							'is_can_delete'		=> $group->isCanDelete()
						);
		} 
		catch(Mage_Core_Exception $e) 
		{
			$this->_fault('group_not_exists');
		}
	}
	
	public function tree()
	{
		$tree = array();
		
		$websites = $this->websites();
		
		foreach($websites as $website)
		{
			$groups = $this->groups($website['group_ids']);	
			$tree[$website['code']] = $website;
			foreach($groups as $group)
			{
				$stores = $this->stores($group["store_ids"]);
				
				$tree[$website['code']]['groups']['group_'.$group['group_id']] = $group;
				
				foreach($stores as $store)
				{
					$tree[$website['code']]['groups']['group_'.$group['group_id']]['stores'][$store['code']] = $store;
				}
			}
		}

		return $tree;
	}
	
}

?>