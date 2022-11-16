#pragma once

/* Basic parameters for AAM USI clay printing setup */

/*  */
#define dirPin 2 // Signal for direction
#define stepPin 3 // Signal for spining

#define relay_1 4
#define relay_2 7
#define relay_3 8
#define relay_4 12


/* Setting up motor step value */
#define stepPerRevolution 6400
#define dropStep_sand 1100
#define retractStep_sand 300

#define unloadStep 3000
#define afterUnloadStep 500


/* Input signal from UR digital output */
#define urAO_0 53 // Robot Analog signal 0 for extruding 