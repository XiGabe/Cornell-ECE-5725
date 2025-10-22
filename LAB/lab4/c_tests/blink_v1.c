//
//  jfs9, 10/24/15  v2, add variable for altering frequency
//         3/17/17 v3,  v3 add internal timer
//         10/14/17 - verify timing...
//    v8 10/24/2020  use pigpio with gpioSleep / gpioDelay



#include <stdlib.h>
#include <stdio.h>
#include <pigpio.h>
int main (int argc, char** argv)
{
  uint32_t period = 500000;  // set initial period for delay in microsec
  uint32_t start_sec;
  int current_sec;
  float frequency;
  
  if (argc>=2 && atoi(argv[1])>0 ) {  // if we have a positive input value
     period = atoi(argv[1]);
  }
  printf ("Set delay to %d usec. period = %d usec\n",period, period*2);
  frequency = ( (1/((float)period*2)) ) * 1000000;
//  printf ("period = %f, 1/period = %f \n",(period*2), (1/(period/2)) );
  printf ("Frequency = %4.2f Hz\n",frequency);
  
  gpioInitialise() ;
  start_sec = gpioTick(); // get time sample; measured in microsec
  gpioSetMode (13, PI_OUTPUT) ; //  GPIO pin 13
  for (current_sec = 0; (current_sec / 1000000) < 10; current_sec = gpioTick() - start_sec)
  {
    gpioWrite (13, 1) ; gpioDelay (period);
    gpioWrite (13, 0) ; gpioDelay (period) ;
  }
  printf ("stopped at %d seconds\n", current_sec/1000000);
  return 0 ;
}
