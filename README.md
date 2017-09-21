# scoopy
A way for academics and research students to stay on top of research publications (using machine learning)

Currently, Scoopy is a terminal-based interactive RSS reader, but eventually I intend it to use scikit-learn to recommend relevant journal articles.

The default feed list is based on my own research interests. 

## Dependencies:

```
-- Python 3.x
-- feedparser: https://github.com/kurtmckee/feedparser
-- scikit-learn 0.18.1: http://scikit-learn.org
```

## Current usage
```
>> from scoopy import start_interactive_trainer, test_model
>> start_intereactive_trainer()
# You will be taken to the interactive trainer. To exit, press 'q'.

>> test_model()
CORRECT:    Highly improved, non-localized field enhancement enabled by hybrid plasmon of crescent resonator/graphene in infrared wavelength
CORRECT:    Materials science: Nanomagnets boost thermoelectric output
CORRECT:    Ultra-thin infrared metamaterial detector for multicolor imaging applications
CORRECT:    Electric field sensing with liquid-crystal-filled slot waveguide microring resonators
FALSE -VE:  True thermal antenna with hyperbolic metamaterials
FALSE -VE:  Biomimetic spiral grating for stable and highly efficient absorption in crystalline silicon thin-film solar cells
CORRECT:    Large area nanoimprint enables ultra-precise x-ray diffraction gratings
-------
-STATS-
correct   = 95.83333333333334%
false +ve = 0.0%
false -ve = 4.166666666666666%

```
