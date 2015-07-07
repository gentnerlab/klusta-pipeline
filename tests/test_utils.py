def test_get_pen():
    pen = 'Pen01_Rgt_AP2500_ML1400'
    result = {'anterior': 2500, 'hemisphere': 'right', 'index': 1, 'lateral': 1400}
    assert get_pen(pen)==result

def test_get_site():
    site = 'Site01_Z1535'
    result = {'depth': 1535, 'index': 1}
    assert get_site(site)==result

def test_get_epoch():
    epc = 'Epc10_2015-06-23+21-40-11_NO_B'
    result = {'datetime': 'Tue Jun 23 21:40:11 2015', 'index': 10, 'prot': 'NO_B'}
    assert get_epoch(epc)==result

def test_get_info():
    smrx = 'E:\experiments\raw\B957\data\Pen01_Rgt_AP2500_ML1400\Site01_Z1535\Epc10_2015-06-23+21-40-11_NO_B\SubB957Pen01Site01Epc10File01_06-23-15+21-40-13_B957.smrx'
    info = {
        'epoch': {
            'datetime': 'Tue Jun 23 21:40:11 2015',
            'index': 10,
            'prot': 'NO_B',
        },
        'filename': 'SubB957Pen01Site01Epc10File01_06-23-15+21-40-13_B957.smrx',
        'pen': {
            'anterior': 2500,
            'hemisphere': 'right', 
            'index': 1, 
            'lateral': 1400,
        },
        'site': {
            'depth': 1535, 
            'index': 1,
        },
        'subject': 'B957',
    }
    assert get_info(smrx)==info

       
    
def test_get_file_info():
    filename = 'SubB957Pen01Site01Epc10File01_06-23-15+21-40-13_B957.smrx'
    result = {'filename': filename, 'datetime': 'Tue Jun 23 21:40:13 2015'}
    assert get_file_info(filename)==result
    
    
def test_get_file_info_autosav():
    filename = 'AutoSv-012715_18-11-04_000.smrx'
    result = {'filename': filename, 'datetime': 'Tue Jan 27 18:11:04 2015'}
    assert get_file_info(filename)==result