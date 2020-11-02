AVRdude argument for programming


# To write fuses to microcontroller (internal osc)
avrdude -c usbtiny -p atmega328p -U lfuse:w:0xe2:m -U hfuse:w:0xd9:m -U efuse:w:0xff:m

avrdude -c usbtiny -p atmega328p -U flash:w:Minion_2_9_uC.hex
