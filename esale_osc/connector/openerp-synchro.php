<?php
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////                                                                        ////////////////////
////////////////////////      PLEASE CONFIGURE THE RIGHT INCLUDES FOR YOUR CONFIGURATION        ////////////////////

	include("xmlrpcutils/xmlrpc.inc");
	include("xmlrpcutils/xmlrpcs.inc");
	include("../../includes/configure.php");
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

	$con = mysql_pconnect(DB_SERVER, DB_SERVER_USERNAME, DB_SERVER_PASSWORD);
	mysql_select_db(DB_DATABASE);


	function debug($s) {
		$fp = fopen("../../temp/debug.xmlrpc.txt","a");
		fwrite($fp, $s."\n");
		fclose($fp);
	}


	function fixEncoding($in_str) {
//		$arr = array(
//			"Ã±" => "ñ",
//			"Ã©" => "e",
//			"Ã¡" => "a",
//			"Ã³" => "o",
//			"Ãº" => "u",
//			"Ãš" => "u",
//			"Ã“" => "o",
//			"Ã&shy;"=> "i",
//			"º"  => " ",
//			"Âº" => ".",
//			"Âª" => ".",
//			"Â°" => ".",
//			"Â·" => ".",
//			"Ã­-" => "i",
//			"Ã¨" => "e",
//			"Ã"  => "i"
//			);
		$arrfrom = array("Ã±","Ã©","Ã¡","Ã³","Ãº","Ãš","Ã“","Ã&shy;","º","Âº","Âª","Â°","Â·","Ã­-","Ã¨","Ã", "”", "");
		$arrto = array( "ñ","e", "a","a", "o", "u", "u", "o", "i", " ", ".", ".", ".", ".", "i", "e", "i", "''", "''");

		$cur_encoding = mb_detect_encoding($in_str);
		if($cur_encoding == "UTF-8" && mb_check_encoding($in_str,"UTF-8")) {
			return str_replace($arrFrom, $arrTo, $in_str);
		} else {
			fwrite($f,'Sin Encoding UTF-8 en else: ' . str_replace($arrFrom, $arrTo, $in_str) ."\n");
//			return utf8_encode(str_replace($arrFrom, $arrTo, $in_str)); // Use this sentence if your server is WINDOWS
			return str_replace($arrFrom, $arrTo, $in_str);
		}
		fclose($f);
	} // fixEncoding


	function debug_arr($para_arr,$tab='') {
		if (is_array($para_arr)) {
			foreach($para_arr as $key=>$values) {
				debug($tab.'Key :'.$key.' Value :'.$values);
				/*
				if (is_array($values)) {
					$tab.='\t';
					debug_arr($values,$tab);
				}*/
			}
		}
	}


	function get_taxes() {
		$taxes = array();

		$result = mysql_query("select tax_class_id, tax_class_title from tax_class;");
		if ($result) while ($row = mysql_fetch_row($result)) {
			$taxes[] = new xmlrpcval(array(new xmlrpcval($row[0], "int"), new xmlrpcval($row[1], "string")), "array");
		}
		return new xmlrpcresp( new xmlrpcval($taxes, "array"));
	}


	function get_languages() {
		$languages = array();

		$result = mysql_query("select languages_id, name from languages;");
		if ($result) while ($row = mysql_fetch_row($result)) {
			$languages[] = new xmlrpcval(array(new xmlrpcval($row[0], "int"), new xmlrpcval($row[1], "string")), "array");
		}
		return new xmlrpcresp(new xmlrpcval($languages, "array"));
	}


	function get_categories() {
		$categories = array();

		$result = mysql_query("select categories_id, min(language_id) from categories_description group by categories_id;");
		if ($result) while ($row = mysql_fetch_row($result)) {
			$resultb = mysql_query("select categories_id, categories_name from categories_description where categories_id=".$row[0]." and language_id=".$row[1].";");
			if ($resultb and $row = mysql_fetch_row($resultb)) {
				$categories[] = new xmlrpcval(array(new xmlrpcval($row[0], "int"), new xmlrpcval(parent_category($row[0],$row[1]), "string")), "array");
			}
		}
		return new xmlrpcresp( new xmlrpcval($categories, "array"));
	}


	function get_categories_parent($languages) {
		$categories = array();
		$lang_ids = "";

		foreach ($languages as $lang)
			 $lang_ids = $lang.", ";
		$lang_ids = substr($lang_ids, 0, strlen($lang_ids)-2);
		$result = mysql_query("select categories_id, parent_id from categories order by parent_id;");
		if ($result) while ($row = mysql_fetch_row($result)) {
			//debug('Category: ' . $row[0].'-'. $row[1]);
			$cat = array(new xmlrpcval($row[0], "int"), new xmlrpcval($row[1], "int"));
			$resultlang = mysql_query("select categories_id, categories_name from categories_description where categories_id=".$row[0]." and language_id in ($lang_ids);");
			if ($resultlang) while ($rowl = mysql_fetch_row($resultlang)) {
				//debug('Category language: ' .$rowl[1]);
				$cat[] = new xmlrpcval($rowl[1], "string");
			}
			$categories[] = new xmlrpcval($cat, "array");
		}
		return new xmlrpcresp(new xmlrpcval($categories, "array"));
	}

	function get_products($languages, $mini, $maxi) {
		$products = array();
		$prod = array();
		$prod_desc = array();
		$row_product = array();
		$products_description_str = "";
		$products_url_str = "";
		$row_manuf = array();
		$manufacturers_name = "";
		$manuf_url = array();
		$manufacturers_url = "";

		$lang_ids = implode(", ", $languages);
		//debug('Languages ids = '.$lang_ids);
		$result = mysql_query("select products_id,
			products_quantity,
			products_model,
			products_image,
			products_price,
			products_date_added,
			products_last_modified,
			products_date_available,
			products_weight,
			products_status,
			products_tax_class_id,
			manufacturers_id
			from products where products_id >= " . $mini . " and products_id <= " . $maxi . " order by products_id;");
		//debug('IF-WHILE-get_products');
		if ($result) while ($row_product = mysql_fetch_row($result)) {
			$resultcateg = mysql_query("select min(categories_id) from products_to_categories
				where products_id=".$row_product[0]." group by products_id;");
			if ($resultcateg) {
					$row = mysql_fetch_row($resultcateg);
				$prod_cat = $row[0];
				//debug('Product Category: ' .$prod_cat);
			}

			//Get product's manufacturer name
			if ($row_product[11] > 0){
				$resultmanuf = mysql_query("select manufacturers_name from manufacturers where manufacturers_id = ".$row_product[11].";");
				if ($resultmanuf){
					$row_manuf = mysql_fetch_row($resultmanuf);
					if (strlen($row_manuf[0]) > 0)
						$manufacturers_name = $row_manuf[0];
					else
						$manufacturers_name = "";
				}
				//Get product's manufacturer url on each language
				$manuf_url = array();
				$resultmanuflang = mysql_query("select manufacturers_url, languages_id
					from manufacturers_info where manufacturers_id = ".$row_product[11]." and languages_id in (".$lang_ids.");");
				if ($resultmanuflang) while ($row_manuflang = mysql_fetch_row($resultmanuflang)) {
					if (strlen($row_manuflang[0]) == 0)
						$manufacturers_url = "";
					else
						$manufacturers_url = $row_manuflang[0];
					$manuf_url[] = new xmlrpcval(array(
						"languages_id" => new xmlrpcval($row_manuflang[1],"int"),
						"manufacturers_url" => new xmlrpcval($manufacturers_url,"string"),
						), "struct");
				}
			} else {
				$manufacturers_name = "";
				$manuf_url = array();
			}

			$prod = new xmlrpcval(array(
				"products_id" => new xmlrpcval($row_product[0],"int"),
				"products_quantity" => new xmlrpcval($row_product[1],"int"),
				"products_model" => new xmlrpcval(fixEncoding($row_product[2]),"string"),
				"products_image" => new xmlrpcval(fixEncoding($row_product[3]),"string"),
				"products_price" => new xmlrpcval(fixEncoding($row_product[4]),"string"),
				"products_date_added" => new xmlrpcval(fixEncoding($row_product[5]),"string"),
				"products_last_modified" => new xmlrpcval(fixEncoding($row_product[6]),"string"),
				"products_date_available" => new xmlrpcval(fixEncoding($row_product[7]),"string"),
				"products_weight" => new xmlrpcval(fixEncoding($row_product[8]),"string"),
				"products_status" => new xmlrpcval($row_product[9],"int"),
				"products_tax_class_id" => new xmlrpcval($row_product[10],"int"),
				"manufacturers_name" => new xmlrpcval(fixEncoding($manufacturers_name),"string"),
				"categ_id" => new xmlrpcval($prod_cat,"int")), "struct");
			//debug('Product_id: ' . $row_product[0] . '-IMG:' .$row_product[3]. '-CAT:' . $prod_cat);

			// Get product information in different languages
			$prod_desc = array();
			$resultlang = mysql_query("select products_id,
				language_id,
				products_name,
				products_description,
				products_url,
				products_viewed
				from products_description where products_id=".$row_product[0]." and language_id in (".$lang_ids.");");
			if ($resultlang) while ($row_desc = mysql_fetch_row($resultlang)) {
			/*	if (strlen($row_desc[3] == 0))
					$products_description_str = "";
				else
					$products_description_str = $row_desc[3];
				if (strlen($row_desc[4] == 0))
					$products_url_str = "";
				else
					$products_url_str = $row_desc[4];
			*/		
				$prod_desc[] = new xmlrpcval(array(
					//"products_id" => new xmlrpcval($row_desc[0],"int"),
					"language_id" => new xmlrpcval($row_desc[1],"int"),
					"products_name" => new xmlrpcval(fixEncoding($row_desc[2]),"string"),
					"products_description" => new xmlrpcval(fixEncoding($row_desc[3]),"string"),
					"products_url" => new xmlrpcval(fixEncoding($row_desc[4]),"string"),
					"products_viewed" => new xmlrpcval(fixEncoding($row_desc[5]),"string"),
				//debug('Product_id: ' . $row_desc[0] . 'language_id: ' . $row_desc[1] . 'products_name: ' . $row_desc[2]);
			}
			
			// Get product discounts
			$prod_spec = new xmlrpcval(array(), "struct"); // If product has not any discount
			$resultspec = mysql_query("select specials_new_products_price,
				specials_date_added,
				specials_last_modified,
				expires_date,
				date_status_change,
				status
				from specials where products_id=". $row_product[0] .
								" and specials_date_added =
								(select max(specials_date_added) from specials where products_id=". $row_product[0] . ");");
			if ($resultspec) {
				$rowesp = mysql_fetch_row($resultspec);
				//debug('Product specials: ' . $rowesp[0] . " " . $rowesp[3]);
				$prod_spec = new xmlrpcval(array(
					"specials_new_products_price" => new xmlrpcval($rowesp[0],"string"),
					//"specials_date_added" => new xmlrpcval($rowesp[1],"string"),
					//"specials_last_modified" => new xmlrpcval($rowesp[2],"string"),
					"expires_date" => new xmlrpcval($rowesp[3],"string"),
					//"date_status_change" => new xmlrpcval($rowesp[4],"string"),
					"status" => new xmlrpcval($rowesp[5],"int")), "struct");
			}

			$products[] = new xmlrpcval(array(
				'product' => $prod,
				'product_description' => new xmlrpcval($prod_desc, "array"),
				'product_special' => $prod_spec,
				'manufacturers_url' => new xmlrpcval($manuf_url, "array"),
				), "struct");
		}
		//debug('END-IF-WHILE-get_products');
		return new xmlrpcresp(new xmlrpcval($products, "array"));
	}

	function get_payment_methods() {
		$payment_methods = array();

		$result_modules = mysql_query("SELECT configuration_value FROM configuration WHERE (configuration_key = 'MODULE_PAYMENT_INSTALLED');");
		if ($result_modules && $row_modules=mysql_fetch_row($result_modules)) {
			$modules = explode(';', $row_modules[0]);
		}
		reset($modules);
		while (list($key, $value) = each($modules)) {
			include("../../includes/modules/payment/".$value);
			include("../../includes/languages/espanol/modules/payment/".$value);
			$class = substr($value, 0, strrpos($value, '.'));
			$obj = new $class();
			$payment_methods[] = new xmlrpcval(array(new xmlrpcval($key, "int"), new xmlrpcval(fixEncoding($obj->title), "string")), "array");
		}
		return new xmlrpcresp( new xmlrpcval($payment_methods, "array"));
	}

	function search_payment_method($payment_name) {
		$languages = array();

		$result_modules = mysql_query("SELECT configuration_value FROM configuration WHERE (configuration_key = 'MODULE_PAYMENT_INSTALLED');");
		if ($result_modules && $row_modules = mysql_fetch_row($result_modules)) {
			$modules = explode(';', $row_modules[0]);
		}

		$result=mysql_query("select directory from languages;");
		if ($result) while ($row=mysql_fetch_row($result)) {
			$languages[] = $row[0];
		}

		reset($modules);
		while (list($key, $value) = each($modules)) {
			foreach ($languages as $lang) {
				$title = "";
				// We must extract the payment method name from the translation file of the payment module
				// We search lines containing the TEXT_TITLE constant like: define('MODULE_PAYMENT_COD_TEXT_TITLE', 'Cash on Delivery');
				$gestor = @fopen("../../includes/languages/$lang/modules/payment/$value", "r");
				if ($gestor) {
					while (!feof($gestor) and $title=="") {
						// Read translation file line by line
						$pieces = explode("'", fgets($gestor));
						if (strpos($pieces[1], "TEXT_TITLE")) {
							$title = $pieces[3];
						}
					}
					fclose ($gestor);
				}
				if ($title == $payment_name) {
					return $key;
				}
			}
		}
		return 0;
	}


	function parent_category($id, $name) {
		$result = mysql_query("select parent_id from categories where categories_id=".$id.";");
		if ($result && $row = mysql_fetch_row($result)) {
			if ($row[0] == 0) {
				return $name;
			} else {
				$resultb = mysql_query("select min(language_id) from categories_description where categories_id=".$row[0].";");
				if ($resultb && $rowb=mysql_fetch_row($resultb)) {
					$resultb = mysql_query("select categories_name from categories_description where categories_id=".$row[0]." and language_id=".$rowb[0].";\n");
					if ($resultb && $rowb=mysql_fetch_row($resultb)) {
						$name = parent_category($row[0], $rowb[0] . " \\ ". $name);
						return $name;
					}
				}
			}
		}
		return $name;
	}


	function set_product_stock($tiny_product) {
		mysql_query("update products set products_quantity=".$tiny_product['quantity']." where products_id=".$tiny_product['product_id'].";");
		mysql_query("update products set products_status=".(($tiny_product['quantity']>0)?1:0)." where products_id=".$tiny_product['product_id'].";");
		return new xmlrpcresp(new xmlrpcval(0,"int"));
	}


	function set_product_manufacturer($tiny_product) {
		$oscom_id = 0;

		if(array_key_exists('manufacturers_name',$tiny_product)) {
			$result = mysql_query("select l.languages_id from languages as l ,configuration as c where
			c.configuration_key='DEFAULT_LANGUAGE' and c.configuration_value=l.code;");

			if ($result && $row = mysql_fetch_row($result)) {
				$lang_id = $row[0];
			}
			$result = mysql_query("select manufacturers_id from manufacturers where (manufacturers_name='".$tiny_product['manufacturers_name']."');");
			if ($result && $row = mysql_fetch_row($result)) {
				$id_exist = 1;
				$oscom_id = $row[0];
			}
			if ($id_exist == 0) {
				mysql_query("insert into manufacturers (manufacturers_name, date_added) values ('".$tiny_product['manufacturers_name']."', now());");
				$oscom_id = mysql_insert_id();
				mysql_query("insert into manufacturers_info (manufacturers_id, languages_id,manufacturers_url) values (".$oscom_id.",".$lang_id.",'".$tiny_product['manufacturers_url']."');");
				foreach ($tiny_product['manufacturer_langs'] as $lang=>$values){
					mysql_query("insert into manufacturers_info (manufacturers_id, languages_id,manufacturers_url) values (".$oscom_id.",".$lang.",'".$values['manufacturers_url']."');");
				}
			} else {
				mysql_query("update manufacturers_info set manufacturers_url='".$tiny_product['manufacturers_url']."' where manufacturers_id=".$oscom_id." and languages_id=".$lang_id.";");
				foreach ($tiny_product['manufacturer_langs'] as $lang=>$values){
					mysql_query("delete from manufacturers_info where manufacturers_id=".$oscom_id." and languages_id=".$lang.";");
					mysql_query("insert into manufacturers_info (manufacturers_id, languages_id,manufacturers_url) values (".$oscom_id.",".$lang.",'".$values['manufacturers_url']."');");
				}
			}
		}
		return $oscom_id;
	}


	function remove_product($tiny_product) {
		if (array_key_exists('oscom_product_ids',$tiny_product)) {
			$i = 0;
			foreach($tiny_product['oscom_product_ids'] as $key=>$values) {
				if($i == 0) {
					$a .= $values;
				} else {
					$a .= ",".$values;
				}
				$i = $i + 1;
			}
			foreach(array('_description','_to_categories','') as $key) {
				mysql_query("delete from products".$key." where products_id in (".$a.");");
			}
		}
		return new xmlrpcresp(new xmlrpcval(1, "int"));
	}


//////////////////////////////////////////////////////////////////////////////////////////////////////////
	function del_spe_price($tiny_val) {
		mysql_query("delete from specials where products_id = ".$tiny_val.";");
		return new xmlrpcresp(new xmlrpcval(1, "int"));
	}


//////////////////////////////////////////////////////////////////////////////////////////////////////////
	function set_product_spe($tiny_product) {
		$lang_id = 1;
		$id_exist = 0;

		////////Check for existance of product_id ///////////
		$result = mysql_query("select products_id from products where (products_id=".$tiny_product['product_id'].");");
		if ($result && $row=mysql_fetch_row($result)) {
			$id_exist = 1;
		}

		$result = mysql_query("select l.languages_id from languages as l configuration as c where c.configuration_key='DEFAULT_LANGUAGE' and c.configuration_value = l.code;");

		if ($result && $row = mysql_fetch_row($result)) {
			$lang_id = $row[0];
		}
		//if ($tiny_product['quantity']>0) {
		//	$tiny_product['status']=1;
		//} else {
		//	$tiny_product['status']=0;
		//}
		$manufacturers_id = set_product_manufacturer($tiny_product);
		if ($id_exist == 0) {
			mysql_query("insert into products (products_quantity, products_model, products_price, products_weight, products_tax_class_id, products_status, manufacturers_id, products_date_added) values (".$tiny_product['quantity'].", '". $tiny_product['model']."', ".$tiny_product['price'].", ".$tiny_product['weight'].", ".$tiny_product['tax_class_id'].", ".$tiny_product['status'].", ".$manufacturers_id.", now());");

			$oscom_id = mysql_insert_id();
			if ( $tiny_product['date_available'] != 'NULL') {
				mysql_query("update products set products_date_available='".$tiny_product['date_available']."' where products_id=".$oscom_id.";");
			}
			mysql_query("insert into specials (products_id, specials_new_products_price, specials_date_added, date_status_change, status) values (".$oscom_id.",".$tiny_product['spe_price'].",now(),now(),".$tiny_product['spe_price_status'].");");
			if ( $tiny_product['exp_date'] != 'NULL') {
				mysql_query("update specials set expires_date='".$tiny_product['exp_date']."' where products_id=".$oscom_id.";");
			}
			mysql_query("insert into products_description (products_id, language_id, products_name, products_description, products_url) values (".$oscom_id.", ".$lang_id.", '".$tiny_product['name']."', '".$tiny_product['description']."', '".$tiny_product['url']."');");
			mysql_query("insert into products_to_categories (categories_id, products_id) values(".$tiny_product['category_id'].",".$oscom_id.");");
			foreach ($tiny_product['langs'] as $lang=>$values) {
				mysql_query("insert into products_description(products_id, language_id, products_name, products_description, products_url)
				values (".$oscom_id.", ".$lang.", '".$values['name']."', '".$values['description']."', '".$values['url']."');");
			}
		} else {
			$oscom_id = $tiny_product['product_id'];
			foreach (array('quantity', 'price', 'weight', 'tax_class_id', 'status', 'date_available') as $key) {
				if ($key == 'date_available' and $tiny_product[$key] != 'NULL') {
					mysql_query("update products set products_".$key."='".$tiny_product[$key]."' where products_id=".$oscom_id.";");
				} else {
					mysql_query("update products set products_".$key."=".$tiny_product[$key]." where products_id=".$oscom_id.";");
				}
			}
			mysql_query("delete from specials where products_id=".$oscom_id.";");
			mysql_query("insert into specials (products_id, specials_new_products_price, specials_date_added, date_status_change, status) values (".$oscom_id.",".$tiny_product['spe_price'].",now(),now(),".$tiny_product['spe_price_status'].");");
			if ( $tiny_product['exp_date'] != 'NULL') {
				mysql_query("update specials set expires_date='".$tiny_product['exp_date']."' where products_id=".$oscom_id.";");
			}

			mysql_query("update products set products_model='".$tiny_product['model']."', manufacturers_id=".$manufacturers_id." where products_id=".$oscom_id.";");

			foreach (array('name', 'description','url') as $key) {
				mysql_query("update products_description set products_".$key."='".$tiny_product[$key]."' where products_id=".$oscom_id." and language_id=".$lang_id.";");
			}
			mysql_query("update products_to_categories set categories_id=".$tiny_product['category_id']." where products_id=".$oscom_id.";");
			foreach ($tiny_product['langs'] as $lang=>$values) {
				mysql_query("delete from products_description where products_id=".$oscom_id." and language_id=".$lang.";");
				mysql_query("insert into products_description(products_id, language_id, products_name, products_description, products_url)
				values (".$oscom_id.", ".$lang.", '".$values['name']."', '".$values['description']."', '".$values['url']."');");
			}
		}

		$cpt = 0;
		if ($tiny_product['haspic']==1) {
			if (file_exists('../../images/'.$cpt.'-'.$tiny_product['fname'])) {
				unlink('../../images/'.$cpt.'-'.$tiny_product['fname']); // DELETE THE EXISTING IMAGES
			}
			if ($hd = fopen('../../images/'.$cpt.'-'.$tiny_product['fname'], "w")) {
				fwrite($hd, base64_decode($tiny_product['picture']));
				fclose($hd);
				mysql_query("update products set products_image='".$cpt."-".$tiny_product['fname']."' where products_id=".$oscom_id.";");
			}
		} else if ($tiny_product['haspic']==2) {
			if (file_exists('../../images/'.$cpt.'-'.$tiny_product['fname'])) {
				unlink('../../images/'.$cpt.'-'.$tiny_product['fname']); // DELETE THE EXISTING IMAGES
			}
			mysql_query("update products set products_image='".$tiny_product['fname']."' where products_id=".$oscom_id.";");
		} else {
			mysql_query("update products set products_image=NULL where products_id=".$oscom_id.";");
		}
		return new xmlrpcresp(new xmlrpcval($oscom_id, "int"));
	}


////////////////////////////////////////////////////////////////////////////////////////////////////
	function set_product_classical($tiny_product) {
		$lang_id = 1;
		$id_exist = 0;

		////////Check for existance of product_id ///////////
		$result = mysql_query("select products_id from products where (products_id=".$tiny_product['product_id'].");");
		if ($result && $row=mysql_fetch_row($result)) {
			$id_exist = 1;
		}
		$result = mysql_query("select l.languages_id from languages as l configuration as c where c.configuration_key='DEFAULT_LANGUAGE' and c.configuration_value=l.code;");

		if ($result && $row = mysql_fetch_row($result)) {
			$lang_id = $row[0];
		}
		//if ($tiny_product['quantity']>0) {
		//	$tiny_product['status']=1;
		//} else {
		//	$tiny_product['status']=0;
		//}
		$manufacturers_id = set_product_manufacturer($tiny_product);
		if ($id_exist == 0) {
			mysql_query("insert into products (products_quantity, products_model, products_price, products_weight, products_tax_class_id, products_status, manufacturers_id, products_date_added) values (".$tiny_product['quantity'].", '". $tiny_product['model']."', ".$tiny_product['price'].", ".$tiny_product['weight'].", ".$tiny_product['tax_class_id'].", ".$tiny_product['status'].", ".$manufacturers_id.", now());");

			$oscom_id = mysql_insert_id();
			if ( $tiny_product['date_available'] != 'NULL') {
				mysql_query("update products set products_date_available='".$tiny_product['date_available']."' where products_id=".$oscom_id.";");
			}
			mysql_query("insert into products_description (products_id, language_id, products_name, products_description, products_url) values (".$oscom_id.", ".$lang_id.", '".$tiny_product['name']."', '".$tiny_product['description']."', '".$tiny_product['url']."');");
			mysql_query("insert into products_to_categories (categories_id, products_id) values(".$tiny_product['category_id'].",".$oscom_id.");");
			foreach ($tiny_product['langs'] as $lang=>$values) {
				mysql_query("insert into products_description(products_id, language_id, products_name, products_description, products_url)
				values (".$oscom_id.", ".$lang.", '".$values['name']."', '".$values['description']."', '".$values['url']."');");
			}
		} else {
			$oscom_id = $tiny_product['product_id'];
			foreach (array('quantity', 'price', 'weight', 'tax_class_id', 'status', 'date_available') as $key) {
				if ($key == 'date_available' and $tiny_product[$key] != 'NULL') {
					mysql_query("update products set products_".$key."='".$tiny_product[$key]."' where products_id=".$oscom_id.";");
				} else {
					mysql_query("update products set products_".$key."=".$tiny_product[$key]." where products_id=".$oscom_id.";");
				}
			}

			mysql_query("update products set products_model='".$tiny_product['model']."', manufacturers_id=".$manufacturers_id." where products_id=".$oscom_id.";");

			foreach (array('name', 'description','url') as $key) {
				mysql_query("update products_description set products_".$key."='".$tiny_product[$key]."' where products_id=".$oscom_id." and language_id=".$lang_id.";");
			}
			mysql_query("update products_to_categories set categories_id=".$tiny_product['category_id']." where products_id=".$oscom_id.";");
			foreach ($tiny_product['langs'] as $lang=>$values) {
				mysql_query("delete from products_description where products_id=".$oscom_id." and language_id=".$lang.";");
				mysql_query("insert into products_description(products_id, language_id, products_name, products_description, products_url)
				values (".$oscom_id.", ".$lang.", '".$values['name']."', '".$values['description']."', '".$values['url']."');");
			}
		}

		$cpt = 0;
		if ($tiny_product['haspic']==1) {
			if (file_exists('../../images/'.$cpt.'-'.$tiny_product['fname'])) {
				unlink('../../images/'.$cpt.'-'.$tiny_product['fname']); // DELETE THE EXISTING IMAGES
			}
			if ($hd=fopen('../../images/'.$cpt.'-'.$tiny_product['fname'], "w")){
				fwrite($hd, base64_decode($tiny_product['picture']));
				fclose($hd);
				mysql_query("update products set products_image='".$cpt."-".$tiny_product['fname']."' where products_id=".$oscom_id.";");
			}
		} else if ($tiny_product['haspic']==2) {
			if (file_exists('../../images/'.$cpt.'-'.$tiny_product['fname'])) {
				unlink('../../images/'.$cpt.'-'.$tiny_product['fname']); // DELETE THE EXISTING IMAGES
			}
			mysql_query("update products set products_image='".$tiny_product['fname']."' where products_id=".$oscom_id.";");
		} else {
			mysql_query("update products set products_image=NULL where products_id=".$oscom_id.";");
		}
		return new xmlrpcresp(new xmlrpcval($oscom_id, "int"));
	}


	function get_partner_address($address_condition, $email="", $phone="", $fax="") {
		$addresses = array();
		$query = "SELECT address_book_id,CONCAT(entry_firstname,' ',entry_lastname) as name, entry_street_address, entry_suburb, entry_postcode, entry_city, entry_state, entry_country_id, entry_zone_id FROM address_book";

		if (is_array($address_condition)) {
			$where = " where ";
			$flag = true;
			foreach($address_condition as $key=>$values) {
				if ($flag) {
					if (!is_numeric($values)) {
						$where.=$key."='".str_replace("'", "''", $values)."'";
					} else {
						$where.=$key."=".$values;
					}
					$flag=false;
				} else {
					if (!is_numeric($values)) {
						$where.=" and ".$key."='".str_replace("'", "''", $values)."'";
					} else {
						$where.=" and ".$key."=".$values;
					}
				}
			}
			$result = mysql_query($query.$where);
		}
		if ($result) while ($row_address=mysql_fetch_array($result, MYSQL_ASSOC)) {
			$country_data = get_country_detail($row_address['entry_country_id']);
			if ($row_address['entry_state'] != '') {
				$state_name = $row_address['entry_state'];
			} else {
				$state_name = $row_address['entry_zone_id'];
			}
			$state_data = get_state_detail($row_address['entry_country_id'],$state_name);
			$ret_address = array(
				"esale_oscom_id" => new xmlrpcval($row_address['address_book_id'],"int"),
				"name" => new xmlrpcval(fixEncoding($row_address['name']),"string"),
				"street" => new xmlrpcval(fixEncoding($row_address['entry_street_address']),"string"),
				"street2" => new xmlrpcval(fixEncoding($row_address['entry_suburb']),"string"),
				"zip" => new xmlrpcval(fixEncoding($row_address['entry_postcode']),"string"),
				"city" => new xmlrpcval(fixEncoding($row_address['entry_city']),"string"),
				"state" => $state_data,
				"country" => $country_data,
				"email" => new xmlrpcval(fixEncoding($email),"string"),
				"phone" => new xmlrpcval(fixEncoding($phone),"string"),
				"fax" => new xmlrpcval(fixEncoding($fax),"string")
			);
			$addresses[] = new xmlrpcval($ret_address,"struct");
		}
		return new xmlrpcval($addresses,"array");
	}


	function get_customer($cust_id) {
		$ret_partners = array();
		$condition = '';
		$query = "SELECT customers_id, CONCAT(customers_firstname,' ',customers_lastname) as name, customers_email_address, customers_default_address_id, customers_telephone, customers_fax from customers";

		if ($cust_id != 0) {
			$condition = " where customers_id=".$cust_id;
		}
		$result = mysql_query($query.$condition.';');
		if ($result) while ($row_cust=mysql_fetch_array($result, MYSQL_ASSOC)) {
			$addresses = get_partner_address(array('customers_id'=>$row_cust['customers_id']));
			$partner = array();
			$partner['esale_oscom_id'] = new xmlrpcval($row_cust['customers_id'],"int");
			$partner['name'] = new xmlrpcval(fixEncoding($row_cust['name']),"string");
			$partner['addresses'] = $addresses;
			$ret_partners[] = new xmlrpcval($partner,"struct");
		}
		return new xmlrpcresp(new xmlrpcval($ret_partners,"array"));
	}


	function get_country_detail($country_name) {
		$query = "select countries_id, countries_name, countries_iso_code_2, countries_iso_code_3 from countries";
		$ret_country = '0';

		if (!is_numeric($country_name)) {
			if($country_name != '') {
				$result = mysql_query($query." where countries_name='".$country_name."';");
			}
		} else {
			$result = mysql_query($query." where countries_id=".$country_name.";");
		}
		if ($result && $row=mysql_fetch_row($result)) {
			$ret_country = new xmlrpcval( array (
				"esale_oscom_id" => new xmlrpcval($row[0],"int"),
				"name" => new xmlrpcval(fixEncoding($row[1]),"string"),
				"code" => new xmlrpcval(fixEncoding($row[2]),"string"),
				"code3" => new xmlrpcval(fixEncoding($row[3]),"string")
			),"struct");
			return $ret_country;
		}
		return new xmlrpcval($ret_country,'string');
	}


	function get_state_detail($country_id,$state_name) {
		$ret_state = '0';
		$query = "select zone_id, zone_code, zone_name from zones";
		$condition = '';

		if (!is_numeric($state_name)) {
			if ($state_name != '') {
				$condition = " where zone_name='".$state_name."' and zone_country_id=".$country_id;
			}
		} else {
			$condition = " where zone_id=".$state_name." and zone_country_id=".$country_id;
		}
		$result = mysql_query($query.$condition.";");
		if ($result && $row=mysql_fetch_row($result)) {
			$ret_state = new xmlrpcval( array (
				"esale_oscom_id" => new xmlrpcval($row[0],"int"),
				"name" => new xmlrpcval(fixEncoding($row[2]),"string"),
				"code" => new xmlrpcval(fixEncoding($row[1]),"string")
			),"struct");
			return $ret_state;
		}
		$ret_state = new xmlrpcval( array (
			"esale_oscom_id" => new xmlrpcval(0,"int"),
			"name" => new xmlrpcval(fixEncoding($state_name),"string"),
			"code" => new xmlrpcval('',"string")
		),"struct");
		return $ret_state;
	}


	function get_saleorders($last_so) {
		$saleorders = array();

		$result = mysql_query("SELECT `orders_id` , `customers_name` , `customers_street_address` , `customers_city` , `customers_postcode` , `customers_state` , `customers_country` , `customers_telephone` , `customers_email_address` , `delivery_name` , `delivery_street_address` , `delivery_city` , `delivery_postcode` , `delivery_state` , `delivery_country` , `billing_name` , `billing_street_address` , `billing_city` , `billing_postcode` , `billing_state` , `billing_country` , `date_purchased` , `orders_status`, `customers_id`, `payment_method`, `customers_id`,`customers_company`,`delivery_company`,`billing_company` FROM `orders` where (orders_id > ".$last_so." and orders_status = 1);");

		if ($result){
			while ($row = mysql_fetch_row($result)) {
				$shopping_price = 0;
				$result_shopping = mysql_query("SELECT value, title from orders_total where class='ot_shipping' and orders_id=".$row[0].";");
				if ($result_shopping && $row_shopping=mysql_fetch_row($result_shopping)) {
					$shopping_price = $row_shopping[0];
					$shipping_title = $row_shopping[1];
				}
				$dcoupon_price = 0;
				$result_coupon = mysql_query("SELECT value, title from orders_total where class='ot_discount_coupon' and orders_id=".$row[0].";");
				if ($result_coupon && $row_coupon=mysql_fetch_row($result_coupon)) {
					$dcoupon_price = $row_coupon[0];
					$dcoupon_title = $row_coupon[1];
				}
				$cash_price = 0;
				$result_cash = mysql_query("SELECT value, title from orders_total where class='ot_fixed_payment_chg' and orders_id=".$row[0].";");
				if ($result_cash && $row_cash=mysql_fetch_row($result_cash)) {
					$cash_price = $row_cash[0];
					$cash_title = $row_cash[1];
				}

				$result_customer = mysql_query("SELECT customers_email_address, customers_telephone, customers_fax FROM customers WHERE customers_id=".$row[25].";");
				if ($result_customer && $row_customer=mysql_fetch_row($result_customer)) {
					$email = $row_customer[0];
					$phone = $row_customer[1];
					$fax = $row_customer[2];
				}
				$default_condition = array("customers_id"=>$row[25],
							"entry_company"=>$row[26],
							"CONCAT(entry_firstname,' ',entry_lastname)"=>$row[1],
							"entry_street_address"=>$row[2],
							"entry_city"=>$row[3],
							"entry_postcode"=>$row[4]
							);
				$default_address = get_partner_address($default_condition, $email, $phone, $fax);
				$delivery_condition = array("customers_id"=>$row[25],
							"entry_company"=>$row[27],
							"CONCAT(entry_firstname,' ',entry_lastname)"=>$row[9],
							"entry_street_address"=>$row[10],
							"entry_city"=>$row[11],
							"entry_postcode"=>$row[12]
							);
				$delivery_address = get_partner_address($delivery_condition, $email, $phone, $fax);
				$billing_condition = array("customers_id"=>$row[25],
							"entry_company"=>$row[28],
							"CONCAT(entry_firstname,' ',entry_lastname)"=>$row[15],
							"entry_street_address"=>$row[16],
							"entry_city"=>$row[17],
							"entry_postcode"=>$row[18]
							);
				$billing_address = get_partner_address($billing_condition, $email, $phone, $fax);
				$result_status = mysql_query("select orders_status_name from orders_status where orders_status_id = " . $row[22].";");
				if ($result_status && $row_status=mysql_fetch_row($result_status)) {
							 $status = $row_status[0];
				}
				$orderlines = array();
				$resultb = mysql_query("select products_id, products_quantity, products_price, products_tax, products_name, orders_products_id from orders_products where orders_id=".$row[0].";");
				if ($resultb){
					while ($rowb = mysql_fetch_row($resultb)) {
						$values_array = array("product_id" => new xmlrpcval($rowb[0], "int"),
							"product_qty" => new xmlrpcval($rowb[1], "int"),
							"price" => new xmlrpcval($rowb[2], "double"),
							"tax_rate" => new xmlrpcval($rowb[3],"double"),
							"name" => new xmlrpcval(fixEncoding($rowb[4]),"string"));
						$result_orders_product_attributes = mysql_query("select products_options, products_options_values, options_values_price, price_prefix from orders_products_attributes where orders_id=".$row[0]." and orders_products_id=".$rowb[5].";");
						if($result_orders_product_attributes && $row_orders_product_attributes= mysql_fetch_row($result_orders_product_attributes)) {
							$orders_product_attributes = new xmlrpcval( array(
								"products_options" => new xmlrpcval(fixEncoding($row_orders_product_attributes[0]),"string"),
								"products_options_values" => new xmlrpcval(fixEncoding($row_orders_product_attributes[1]),"string"),
								"options_values_price" => new xmlrpcval($row_orders_product_attributes[2],"double"),
								"price_prefix" => new xmlrpcval(fixEncoding($row_orders_product_attributes[3]),"string")), "struct");
							$values_array["attributes"] = $orders_product_attributes;
						}
						$orderlines[] = new xmlrpcval($values_array, "struct");
			 		}
				}
				$note = "";
				$result_comments = mysql_query("select comments FROM orders_status_history where (orders_id = ".$row[0]." and orders_status_id = 1);");
				if ($result_comments && $row_comments=mysql_fetch_row($result_comments)) {
					$note=$row_comments[0];
				}
//				$result_price_with_tax = mysql_query("SELECT configuration_value FROM configuration where (configuration_key = 'DISPLAY_PRICE_WITH_TAX');");
//				if ($result_price_with_tax && $row_price_with_tax=mysql_fetch_row($result_price_with_tax)) {
//					if ($row_price_with_tax[0] == 'false') {
						$price_type="tax_excluded";
//					} else {
//						$price_type="tax_included";
//					}
//				}
				$saleorders[] = new xmlrpcval( array("id" => new xmlrpcval( $row[0], "int"),
					"price_type" => new xmlrpcval( fixEncoding($price_type), "string" ),
					"note" => new xmlrpcval(fixEncoding($note), "string" ),
					"lines" => new xmlrpcval( $orderlines, "array"),
					"pay_met" => new xmlrpcval( search_payment_method($row[24]), "int"),
					"pay_met_title" => new xmlrpcval( fixEncoding($row[24]), "string"),
					"shipping_price" => new xmlrpcval( $shopping_price, "double"),
					"shipping_title" => new xmlrpcval(fixEncoding($shipping_title), "string"),
					"dcoupon_price" => new xmlrpcval( $dcoupon_price, "double"),
					"dcoupon_title" => new xmlrpcval(fixEncoding($dcoupon_title), "string"),
					"cash_price" => new xmlrpcval( $cash_price, "double"),
					"cash_title" => new xmlrpcval(fixEncoding($cash_title), "string"),
					"orders_status" => new xmlrpcval( fixEncoding($status), "string"),
					"partner" => get_customer($row[25]),
					"date" => new xmlrpcval( $row[21], "string"),
					"address" => $default_address,
					"delivery" => $delivery_address,
					"billing" => $billing_address
				), "struct");
			}
		}
		return new xmlrpcresp(new xmlrpcval($saleorders, "array"));
	}


	function get_min_open_orders($last_so) {
		$result = mysql_query("SELECT min(`orders_id`) as min FROM `orders` where (orders_id <= ".$last_so.") and (orders_status = 2);");
		if ($result) {
			$min = mysql_fetch_row($result);
			return new xmlrpcresp( new xmlrpcval($min[0], "int"));
		} else
				return new xmlrpcresp( new xmlrpcval(-1, "int"));
	}


	
	function get_max_products_id() {
		$result = mysql_query("SELECT max(`products_id`) as max FROM `products`;");
		if ($result) {
			$max = mysql_fetch_row($result);
			return new xmlrpcresp( new xmlrpcval($max[0], "int"));
		} else
				return new xmlrpcresp( new xmlrpcval(-1, "int"));
	}

	function get_min_products_id() {
		$result = mysql_query("SELECT min(`products_id`) as min FROM `products`;");
		if ($result) {
			$min = mysql_fetch_row($result);
			return new xmlrpcresp( new xmlrpcval($min[0], "int"));
		} else
			return new xmlrpcresp( new xmlrpcval(-1, "int"));
	}


	function close_open_orders($order_id) {
		mysql_query("update orders set orders_status=3 where orders_id=".$order_id.";");
		return new xmlrpcresp(new xmlrpcval(0, "int"));
	}


	function process_order($order_id) {
		mysql_query("update orders set orders_status=2 where orders_id=".$order_id.";");
		return new xmlrpcresp(new xmlrpcval(0, "int"));
	}


	$server = new xmlrpc_server( array(	"get_taxes" => array(		"function" => "get_taxes",
																	"signature" => array(	array($xmlrpcArray)
																						)
																	),
										"get_languages" => array(	"function" =>	"get_languages",
																	"signature" => array(	array($xmlrpcArray)
																						)
																	),
										"get_categories" => array(	"function" =>	"get_categories",
																	"signature" =>	array(	array($xmlrpcArray)
																						)
																	),
										"get_categories_parent" => array(	"function" =>	"get_categories_parent",
																	"signature" =>	array(	array($xmlrpcArray, $xmlrpcArray)
																						)
																	),
										"get_products" => array(	"function" =>	"get_products",
																	"signature" =>	array(	array($xmlrpcArray, $xmlrpcArray, $xmlrpcInt, $xmlrpcInt)
																						)
																	),																														
										"get_payment_methods" => array(	"function" =>	"get_payment_methods",
																		"signature" =>	array(	array($xmlrpcArray)
																						)
																	),
										"get_saleorders" => array(	"function" =>	"get_saleorders",
																	"signature" =>	array(	array($xmlrpcArray, $xmlrpcInt)
																						)
																	),
										"get_min_products_id" => array( "function" =>	"get_min_products_id",
																	"signature" => array( array($xmlrpcInt)
																						)
																	),
										"get_max_products_id" => array( "function" =>	"get_max_products_id",
																	"signature" => array( array($xmlrpcInt)
																						)
																	),
										"get_min_open_orders" => array(	"function" =>	"get_min_open_orders",
																	"signature" =>	array(	array($xmlrpcInt, $xmlrpcInt)
																						)
																	),
										"set_product_spe" => array(		"function" =>	"set_product_spe",
																	"signature" =>	array(	array($xmlrpcInt, $xmlrpcStruct)
																						)
																	),
										"set_product_classical" => array(		"function" =>	"set_product_classical",
																	"signature" =>	array(	array($xmlrpcInt, $xmlrpcStruct)
																						)
																	),
										"remove_product" => array(		"function" =>	"remove_product",
																	"signature" =>	array(	array($xmlrpcInt, $xmlrpcStruct)
																						)
																	),
										"del_spe_price" => array(		"function" =>	"del_spe_price",
																	"signature" =>	array(	array($xmlrpcInt, $xmlrpcInt)
																						)
																	),
										"set_product_stock" => array(	"function" =>	"set_product_stock",
																		"signature" =>	array(	array($xmlrpcInt, $xmlrpcStruct)
																						)
																	),
										"process_order" => array(		"function" =>	"process_order",
																		"signature" =>	array(	array($xmlrpcInt, $xmlrpcInt)
																						)
																	),
										"close_open_orders" => array(	"function" =>	"close_open_orders",
																		"signature" =>	array(	array($xmlrpcInt, $xmlrpcInt)
																						)
																	),
										"get_customer" => array(	"function" =>	"get_customer",
																		"signature" =>	array(	array($xmlrpcArray, $xmlrpcInt)
																						)
																	)

										), false);
	$server->functions_parameters_type = 'phpvals';
	$server->service();
?>
