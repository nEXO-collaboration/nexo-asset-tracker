import barcode
from barcode.writer import ImageWriter

def testEan():
    EAN = barcode.get_barcode_class('ean13')
    ean = EAN(u'5679004263734-001', writer=ImageWriter())
    fullname = ean.save('my_ean13_barcode')

testEan()

