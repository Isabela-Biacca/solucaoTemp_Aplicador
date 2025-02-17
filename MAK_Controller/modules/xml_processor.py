import xml.etree.ElementTree as ET

def get_production_order(xml_path: str) -> tuple:
    try:
        tree = ET.parse(xml_path)
        ns = {'ns0': 'http://www.wbf.org/xml/B2MML-V0401'}
        op = tree.find(".//ns0:ProductionSchedule/ns0:ID", ns).text
        creation_date = tree.find(".//ns0:ApplicationArea/ns0:CreationDateTime", ns).text
        sku = tree.find('.//ns0:MaterialRequirement/ns0:MaterialDefinitionID', ns).text
        linha = tree.find('.//ns0:SegmentRequirement/ns0:Location/ns0:EquipmentID', ns).text
        linha_tratada = linha.lstrip("Z")
        return op, creation_date, sku, linha_tratada
    except Exception as e:
        raise ValueError(f"Erro no XML {xml_path}: {str(e)}")