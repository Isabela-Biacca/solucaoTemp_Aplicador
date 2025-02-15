import xml.etree.ElementTree as ET

def get_production_order(xml_path: str) -> tuple:
    try:
        tree = ET.parse(xml_path)
        ns = {'ns0': 'http://www.wbf.org/xml/B2MML-V0401'}
        order_id = tree.find(".//ns0:ProductionSchedule/ns0:ID", ns).text
        creation_date = tree.find(".//ns0:ApplicationArea/ns0:CreationDateTime", ns).text
        sku = tree.find('.//ns0:MaterialRequirement/ns0:MaterialDefinitionID', ns).text
        return order_id, creation_date, sku
    except Exception as e:
        raise ValueError(f"Erro no XML {xml_path}: {str(e)}")