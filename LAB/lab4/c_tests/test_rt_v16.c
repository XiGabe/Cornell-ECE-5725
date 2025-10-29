//
// jfs9 10/24/15
// v2 Add wiringPi to toggle output
// v5 10/22/18 - add frequency display
// v6 10/22/18 - loop not nanosleep
// v16 10/24/2020 - convert from wiringpi to pigpio
//  		clean up some unused vars and code
//     10/10/2021   check 		
//     3/28/2022    check
//     3/15/2024 check
//     10/20/2024  check
//     3/20/2025
//

#include <stdlib.h>
#include <stdio.h>
#include <time.h>
#include <sched.h>
#include <sys/mman.h>
#include <string.h>
#include <pigpio.h>


#define MY_PRIORITY (49) /* we use 49 as the PRREMPT_RT use 50
                            as the priority of kernel tasklets
                            and interrupt handler by default */

#define MAX_SAFE_STACK (8*1024) /* The maximum stack size which is
                                   guaranteed safe to access without
                                   faulting */

#define NSEC_PER_SEC    (1000000000) /* The number of nsecs per sec. */

void stack_prefault(void) {

        unsigned char dummy[MAX_SAFE_STACK];

        memset(dummy, 0, MAX_SAFE_STACK);
        return;
}

int main(int argc, char* argv[])
{
        struct sched_param param;
        int interval = 500000000; /* long delay */
        int PinValue = 0;  // used to toggle output pin
        int i;
        int GpioPin = 26; // <--- [修改] 定义GPIO引脚（使用13作为示例）


       if ( argc>=2 && atoi(argv[1] ) >0 ) { // if positive argument
          interval = atoi(argv[1]);
       }
       printf ( "Interval = %d loops\n", interval);

        gpioInitialise();   // initialize pigpio 
        gpioSetMode(GpioPin, PI_OUTPUT);  // set GpioPin = OUTPUT [cite: 608]

        /* Declare this as a real time task */
/****/
        param.sched_priority = MY_PRIORITY;
        if(sched_setscheduler(0, SCHED_FIFO, &param) == -1) {
                perror("sched_setscheduler failed");
                exit(-1);
        }
/****/
        /* Lock memory */

        if(mlockall(MCL_CURRENT|MCL_FUTURE) == -1) {
                perror("mlockall failed");
                exit(-2);
        }

        /* Pre-fault our stack */

        stack_prefault();

         while(1) {

               for ( i=0 ; i<interval ; ++i ) {  /// use delay loop to control frequency
                   // interval 1200 = about 60k Hz
               }

               // Set the GPIO pin to the current value (0 or 1)
               gpioWrite(GpioPin, PinValue); 
               
               // Toggle the value for the next loop iteration
               PinValue = 1 - PinValue;
   }
}