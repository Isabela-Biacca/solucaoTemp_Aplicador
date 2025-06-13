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
    
def get_lpn_values(xml_path: str) -> tuple:
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        
        # Definir os namespaces usados no XML
        ns = {
            'soap': 'http://schemas.xmlsoap.org/soap/envelope/',
            'b2mml': 'http://www.wbf.org/xml/B2MML-V0401'
        }
        
        # Buscar os campos usando os namespaces
        creation_date = root.find('.//b2mml:CreationDateTime', ns).text
        numLpn = root.find('.//b2mml:MaterialSubLotID', ns).text
        op = root.find('.//b2mml:ProductionScheduleID', ns).text
        sku = root.find('.//b2mml:MaterialDefinitionID', ns).text
        
        return op, creation_date, sku, numLpn
    except Exception as e:
        raise ValueError(f"Erro no XML {xml_path}: {str(e)}")   