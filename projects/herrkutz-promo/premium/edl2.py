# Frame-exact EDL @30fps. (frames, src_in, speed, grade, note)
# Hidden source cuts (scene detect): 2.867, 4.300, 9.933, 15.167, 25.067, 32.600, 33.467
EDL=[
 (135, 0.00, 2.55/4.5, "before","BEFORE oner: long hair, cape, neck strip (src 0.00-2.55)"),
 ( 30, 3.00, 1.0,  "warm","Barber pole (src 3.00-4.00)"),
 ( 30, 4.40, 1.0,  "warm","Scissors up, HERRKUTZ chair (4.40-5.40)"),
 ( 30, 6.20, 1.0,  "warm","Comb + shears at crown (6.20-7.20)"),
 ( 60, 7.90, 1.0,  "warm","Barber shaping, one shot (7.90-9.90)"),
 ( 68,12.88, 1.0,  "warm","Wide to tight clipper, one shot (12.88-15.147)"),
 ( 15,10.60, 1.0,  "warm","Whip-pan to ceiling (10.60-11.10)"),
 ( 90,29.55, 1.0,  "warm","Walk-through oner: floor, barber smile, push to client (29.55-32.55)"),
 ( 75,32.62, 0.30, "hero","AFTER reveal, slow motion (32.62-33.37)"),
 (127, None, None, "split","Split BEFORE 0.30 / AFTER 32.80"),
 ( 38,15.20, 0.50, "warm","Night sign (15.20-15.83)"),
 ( 60,26.50, 1.0,  "warm","Hand pushes the door open (26.50-28.50)"),
 (142,18.00, 0.50, "end","End card storefront (18.00-20.37)"),
]
assert sum(e[0] for e in EDL)==900
