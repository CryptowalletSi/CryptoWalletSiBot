import logging
log = logging.getLogger('util')

def round_price(p):
    places = 4
    if p < 0.1:
        places = 5
    if p < 0.001:
        places = 6
    if p < 0.0001:
        places = 8
    return ("{:." + str(places) + "f}").format(round(p * (10**places)) / (10**places))
        

