# A Simple and Fun Game #

**Sbonu** is meant to be a fun game to play, in addition to illustrating the action of viral memes in a population.

To begin with the game will be kept as simple as possible.  We can add in more complex behaivor later on.

The game is currently extremely "fresh", not really in a ready to run state, although if you run just the sbonu.py script by itself you should see a crude ascii output simulation run.

```
   f      f     O         O      f

      .        O                        f
    O  O       .               .              2
    .                           O
                          f
                   O               2
               O
O O  f         .                    .     f
O.         f  ..          O        O             f
              O          f .  f
                                   f  O
                                       .
       .                                .O f
        O                                       O
f         O  .O       f
     .    .                 f                  .O
      O          O
           .                     f     O .
      f     *                             O  f
                               O                 .
                  .       f   .                  O
                 2            .
                 .O.                   O
      2  *OO f                   O             f
f          .                     .
                       f           O .
                                  .   .O
                                            .O   O
          f                                  O  .
     f           f
                                        f
f                     f          f               f

                            f
  O        O
  .             O                     f
                       O                   f

      O
         .                   f
        O  f                                    O
 f                      f        O     f
                  f             .
                                          O
                                         .
                              f

f                        f                   .
      O       f    f               f   .      O    0.03 0.00 00069
```
_a early stage of a meme infection, only 3% of the population has it._

**Legend**
| `0` | Unaffected NPC |
|:----|:---------------|
| `*` | Meme-carrying NPC |
| `2` - `9` | More than one person on the same spot |
| `+` | More than 9 people on the same spot |
| `f` | Food units |
| `.` | _Slime trail_ of an NPC's immediate past location |

and the three numbers are:
| Percent carrying meme | Percent immune | generations |
|:----------------------|:---------------|:------------|
| 0.03 | 0.00 | 00069 |


Once the engine (see below) works, I want to use pygame to give it a cool UI and try to make it actually fun.

## Software Architecture ##

The software has three layers:

  1. **Simulator** - A simple simulator (probably using MyHDL but perhaps Stackless Python) that models a field of "food" and a population of "NPCs" who live there.
  1. **UI** - Provides events that allows various "views" and/or "controllers" (in the MVC sense) to visualize the running sim and interact with it.
  1. **GUIs** - Several different "frontends" to permit interaction with the sim, thus making it a game.  I.e. Tkinter, curses, PyGame, graph rendering, &c.





