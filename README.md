# Roguelike: Labyrinth
Simple roguelike dungeon exploration game. Current features are 
maze navigation and forward progression through endoless levels.

## Level design
Levels are all generated using Prim's algorithm. A maze style I find aesthecically appealing and a good balance between fun and challanging to navigate through.

Prim's algorithm is quite easy to conceptually understand and an elegant method of creating mazes. There are plenty of examples online to assist with understanding how it may be executed in code but none that I found that render the final maze with walls that possess thickness - A typical feature of roguelike game maps rendered with ascii graphics.

## Field of view
Recursive shadow casting is used to calculate field of view. Finding the popular Roguebasin code somewhat confusing, I opted to write a version from scratch to gain a better understanding. Along with the code, Roguebasin provides an excellent overview of the shadow casting process. Combined with a writeup on adammil.net (particularly the diagrams showing angles of sight) I was able to gain a good theoretical understanding and successfully write my own algorithm.

+ [Roguebasin](http://www.roguebasin.com/index.php?title=FOV_using_recursive_shadowcasting)
+ [adammil.net](http://www.adammil.net/blog/v125_Roguelike_Vision_Algorithms.html#intro)

## Further Development

### The initial goals of this project

+ Practice Python and coding in general
+ Attempt to implement Prim's algorithm
+ Create a basic navigable roguelike game

### Further potential features:

+ Path finding using A* and Dijkstra algorithms