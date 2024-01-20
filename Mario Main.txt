#   memory allocation table
#   {
#       {0 -> 255}: x 8 table, size = 256
#       {256 -> 511}: array pointer lookup table [ takes an input i, multiplies it by 13 and adds an offset ~512 to the appropriate location of the level data], size = 256 (roughly the number of block colums in the level)
#       {512 -> 4095}: level data, size = 3584, for rendering
#       {4096 -> 4159}: variables, size = 64
#       {
#           @ 4096: player x (pixel remainer)
#           @ 4097: player x (blocks)
#           @ 4098: player y (pixel remainder)
#           @ 4099: player y (blocks)
#           @ 4100: player x vel (pixels/s)
#           @ 4101: player y vel (pixels/s)
#           @ 4102: player status grounded
#           @ 4103: wall x (pixel remainder)
#           @ 4104: wall x (blocks)
#           @ 4105: wall y (pixel remainer)
#           @ 4106: wall y (blocks)
#
#           @ 4107: previous player_x (pixels)
#           @ 4108: previous player_y (pixels)
#           @ 4109: current player_x (pixels)
#           @ 4110: current player_y (pixels)
#
#           @ 4111: wall_x (pixels)
#           @ 4112: wall_y (pixels)
#       }
#       {4160 -> 7231}: level data 2, size = 3072, for collision detection and other game logic
#       {16384 -> 16639}: 256 mult table, size = 256, for x axis mult when calculating screen pos vector
#       {16640 -> 16928}: mult talbe {-8 -> 8} * {-8 -> 8} for collision detection alg, size = 289
#       {63488 -> 65535}: stack, size = 2048 # arbituary, may be overrun but extremely unlikely ~ 0 probability
#
#   }

.innit                  ldi r7, 1
                        str r7, 4102    # grounded              

.main_loop              mov r0, r0

.input                  pld r5, p4      # load input
                        lod r1, 4100    # x-velocity
                        lod r2, 4101    # y-velocity
                        ldi r6, 1
                        and r6, r6, r5
                        xor r0, r6, r5
                        jif z .left
.test_input_right       ldi r6, 2
                        and r6, r6, r5
                        xor r0, r6, r5
                        jif z .right
.test_input_jump        ldi r4, 4
                        and r6, r4, r5
                        xor r0, r6, r5
                        jif z .jump
                        jmp .physics

                        # 1 -> left
                        # 2 -> right
                        # 4 -> jump

.left                   sbc r1, r1, r0
                        jif n +2
                        jmp .test_input_right
                        ldi r7, 0b1111111111110111 # -8
                        cmp r1, r7  
                        jif gr .test_input_right    # allows -8
                        str r7, 4100
                        jmp .test_input_right

.right                  adc r1, r1, r0
                        ldi r7, 8
                        cmp r1, r7
                        jif le .test_input_jump
                        str r7, 4100
                        jmp .test_input_jump

.jump                   lod r7, 4102 # grounded status
                        and r7, r7, r7
                        jif z, .physics
                        ldi r3, 8
                        str r3, 4101
                        str r0, 4102

.physics                ldi r7, 3
                        and r0, r5, r7
                        jif z .friction
.?gravity               lod r7, 4102
                        and r7, r7, r7
                        jif z .gravity
                        jmp .update
                                       
.friction               and r1, r1, r1
                        jif n .fn
                        jif z .?gravity
                        sbc r1, r1, r0
                        str r1, 4100
                        jmp .?gravity
.fn                     add r1, r1, r0
                        str r1, 4100
                        jmp .?gravity
                         
.gravity                and r2, r2, r2
                        jif n +2
                        jmp .update
                        ldi r7, 0b1111111111110111 # -8
                        cmp r2, r7
                        jif gr .update
                        sbc r2, r2, r0
                        str r2, 4101

.update                 lod r3, 4109    # player_x (current)
                        lod r4, 4110    # player_y (current)
                        str r3, 4107    # current -> previous for collision
                        str r4, 4108    
                        # update position
                        add r1, r3, r1
                        add r2, r4, r2
                        # store in current position
                        str r1, 4109
                        str r2, 4110
                        
                        # update  after collision alg for rendering or re-write renderer
                        # @ 4096: player x (pixel remainer)
                        # @ 4097: player x (blocks)
                        # @ 4098: player y (pixel remainder)
                        # @ 4099: player y (blocks)
          
                        # r1 -> curr x
                        # r2 -> curr y


.detect_collision       rsh r7, r1
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r2
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_collision

                        ldi r7, 6   # player_width
                        ldi r6, 7   # player_height

                        add r1, r1, r7

                        rsh r7, r1
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r2
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_collision  

                        add r2, r2, r6

                        rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r2
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_collision

                        sub r1, r1, r7

                        rsh r7, r1
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r2
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_collision
                        # no collision so check wall
                        jmp .wall


                        # look at c code for help lol
                        
                        # r1 = player_x     previous position before update
                        # r2 = player_y
                        # r3 = block_x      current position
                        # r4 = block_y
                        # r5 = x_vel
                        # r6 = y_vel
                        # r7 for temp stuff

                        # r1 has p_x
                        # r2 has p_y

.resolve_collision      psh r1  # corner x
                        psh r2  # corner y

                        lod r1, 4107
                        lod r2, 4108
                        ldi r7, 65528
                        lod r3, 4109
                        lod r4, 4110
                        and r3, r3, r7  # rounding down to nearest 8
                        and r4, r4, r7  # "
                        lod r5, 4100
                        lod r6, 4101

                        sub r0, r0, r5
                        jif n .+x
                        sub r0, r0, r6
                        jif n .-x+y
                        ldi r7, 7
                        add r3, r3 ,r7
                        add r4, r4, r7
                        ldi r7, 8
                        add r5, r5, r7  
                        lfp r7, r5
                        lsh r7, r7
                        add r7, r5, r7
                        add r7, r4, r7
                        sub r7, r7, r2
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7      
                        psh r7
                        ldi r5, 8
                        add r6, r6, r5
                        lfp r7, r6
                        lsh r7, r7
                        add r7, r6, r7
                        add r7, r7, r3
                        sub r7, r7, r1
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7
                        pop r6
                        sub r7, r6, r7

                        jif n .--side

                        rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        adc r7, r6, r7      # +1 -> c code
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        adc r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_x
                        ldi r7, 1
                        str r7, 4102       # grounded call
                        jmp .resolve_y  

.--side                 rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        adc r7, r6, r7      # +1 -> c code
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif z .resolve_x
                        ldi r7, 1
                        str r7, 4102       # grounded call
                        jmp .resolve_y         

.-x+y                   ldi r7, 7
                        add r3, r3, r7
                        ldi r7, 8
                        add r5, r5, r7
                        lfp r7, r5
                        lsh r7, r7
                        add r7, r5, r7
                        add r7, r4, r7
                        sub r7, r7, r2
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7      
                        psh r7
                        ldi r5, 8
                        add r6, r6, r5
                        lfp r7, r6
                        lsh r7, r7
                        add r7, r6, r7
                        add r7, r7, r3
                        sub r7, r7, r1
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7
                        pop r6
                        sub r7, r6, r7

                        jif n .-+bottom

                        rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        adc r7, r6, r7      # +1 -> c code
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif z .resolve_x
                        jmp .resolve_y 

.-+bottom               rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3647        # 512 + 3648 = 4160 -> collision level data matrix, -1 -> c code 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_x
                        jmp .resolve_y             

.+x                     sub r0, r0, r6
                        jif n .+x+y                 
.+x-y                   ldi r7, 7
                        add r4, r4, r7
                        ldi r7, 8
                        add r5, r5, r7  
                        lfp r7, r5
                        lsh r7, r7
                        add r7, r5, r7
                        add r7, r4, r7
                        sub r7, r7, r2
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7      
                        psh r7
                        ldi r5, 8
                        add r6, r6, r5
                        lfp r7, r6
                        lsh r7, r7
                        add r7, r6, r7
                        add r7, r7, r3
                        sub r7, r7, r1
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7
                        pop r6
                        sub r7, r6, r7

                        jif n .+-top

                        rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 255         # -1 -> c code
                        add r7, r6, r7
                        lfp r7, r7  # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif z .resolve_x
                        ldi r7, 1
                        str r7, 4102       # grounded call
                        jmp .resolve_y
 
.+-top                  rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7  # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        adc r7, r7, r5      # +1 -> c code
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_x
                        ldi r7, 1
                        str r7, 4102       # grounded call
                        jmp .resolve_y 

.+x+y                   ldi r7, 8
                        add r5, r5, r7  
                        lfp r7, r5
                        lsh r7, r7
                        add r7, r5, r7
                        add r7, r4, r7
                        sub r7, r7, r2
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7      
                        psh r7
                        ldi r5, 8
                        add r6, r6, r5
                        lfp r7, r6
                        lsh r7, r7
                        add r7, r6, r7
                        add r7, r7, r3
                        sub r7, r7, r1
                        ldi r5, 16648
                        add r7, r5, r7
                        lfp r7, r7
                        pop r6
                        sub r7, r6, r7

                        jif n .++side

                        rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 256
                        add r7, r6, r7
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3647        # 512 + 3648 = 4160 -> collision level data matrix, -1 -> c code 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif n .resolve_x
                        jmp .resolve_y

.++side                 rsh r7, r3
                        rsh r7, r7
                        rsh r7, r7
                        ldi r6, 255
                        add r7, r6, r7      # -1 since c code
                        lfp r7, r7          # x 13 + 512
                        rsh r6, r4
                        rsh r6, r6
                        rsh r6, r6
                        add r7, r6, r7
                        ldi r5, 3648        # 512 + 3648 = 4160 -> collision level data matrix 
                        add r7, r7, r5
                        lfp r7, r7
                        sub r0, r0, r7
                        jif z .resolve_x
                        jmp .resolve_y         

#----# all garbage, redo #----#
# find the difference between the corner and block then add that to the actual player position not the corner.

# set x_vel to zero
# player_x can be r1
# block x can be r3

.resolve_x              pop r2  # corner y
                        pop r1  # corner x
                        sub r7, r3, r1
                        lod r6, 4109        # curr x
                        add r6, r6, r7      # correct position
                        str r0, 4100        # set vel to 0 since collision
                        jmp .wall

# player_y in r2            
# block_y in r4

.resolve_y              pop r2  # corner y
                        pop r1  # corner x
                        sub r7, r4, r2
                        lod r6, 4110        # curr x
                        add r6, r6, r7      # correct position
                        str r0, 4101        # set vel to 0 since collision
                        jmp .wall

# check player hasnt gone of past the left edge of the screen
# if player is past some point, increase the wall pos by the players x velocity

.wall                   lod r1, 4109        # current x
                        lod r2, 4111        # wall x (pixels)
                        cmp r1, r2
                        jif le .left_wall
                        ldi r7, 33
                        add r3, r2, r7
                        cmp r1, r3
                        jif gr .updt_wall
                        jmp .rend_scene
.left_wall              str r2, 4109
                        jmp .wall_block_updt
.updt_wall              sub r4, r3, r1
                        add r2, r2, r4
                        str r2, 4111

                        # make wall pos into blocks for .rend_scene                                          
                        # wall y can just follow player_y

.wall_block_updt        rsh r2, r2
                        rsh r2, r2
                        rsh r2, r2
                        str r2, 4104
                        lod r3, 4110    # player_y
                        rsh r3, r3
                        rsh r3, r3
                        rsh r3, r3
                        str r3, 4106
                        jmp .rend_scene

.rend_scene             ldi r1, 0b0100000000000101 # set up gpu #13
                        pst p1, r1
                        lod r1 4104         # i variable for loop
                        ldi r2, 12
                        add r2, r1, r2      # max i iterator (theoretical)
                        lod r3, 4106
                        ldi r4, 8
                        add r4, r3, r4      # max j
                        jmp .L0             # loop
.L5                     ldi r6, 256
                        add r6, r6, r1
                        lfp r6, r6          # x13 + 512 
                        psh r2
                        lfp r5, r6          # number of items in the list in r5                
                        psh r1
                        adc r6, r6, r0      # ptr to start of block data in r6
                        add r3, r6, r5      # max value of pointer
                        jmp .L2
.L4                     lfp r7, r6          # load block data first 4 bits are the y coord: and 15 with it
                        ldi r1, 15          # r1, r2 free now for temp variables
                        and r1, r7, r1
                        cmp r1, r4          # check if its greater than y limit
                        jif gr .L1          # break from inner loop
                        lod r2, 4106        # base height (blocks)
                        cmp r1, r2
                        jif le .rL3         # if less than base skip draw
                        jmp .call_gpu
.rL3                    adc r6, r6, r0      # loop logic
.L2                     cmp r6, r3
                        jif le .L4
.L1                     pop r1
                        adc r1, r1, r0
                        pop r2
.L0                     cmp r1, r2
                        jif le .L5
                        jmp .update_screen

.call_gpu               sub r7, r7, r1
                        pst p2, r7
                        pop r7
                        mov r0, r0
                        psh r7
                        psh r4
                        lfp r1, r1
                        lod r4, 4112
                        sub r1, r1, r4
                        lfp r7, r7
                        lod r4, 4111
                        sub r7, r7, r4
                        ldi r4, 16384
                        add r7, r7, r4
                        lfp r7, r7
                        adc r1, r1, r7
                        pst p3, r1
                        pop r4
                        jmp .rL3

.update_screen          ldi r3, 0b1000000000000000
                        pst p1, r3
                        ldi r3, 0b1100000000000000
                        pst p1, r3
                        jmp .main_loop



        ; old cpu

        ldi r7, 8
        add r5, r5, r7  
        lfp r7, r5
        lsh r7, r7
        add r7, r5, r7
        add r7, r4, r7
        sub r7, r7, r2
        ldi r5, 16648
        add r7, r5, r7
        lfp r7, r7      
        psh r7
        ldi r5, 8
        add r6, r6, r5
        lfp r7, r6
        lsh r7, r7
        add r7, r6, r7
        add r7, r7, r3
        sub r7, r7, r1
        ldi r5, 16648
        add r7, r5, r7
        lfp r7, r7
        pop r6
        sub r7, r6, r7      ; total = 23 cycles

        ; new cpu code

        sub r10, r4, r2
        ;imul r10, r5        ; 2 cycles
        ;mov r11, mxl
        sub r10, r3, r11
        ;imul r10, r6        ; 2 cycles
        ;sub r7, r11, mxl    ; total = 8 cycles

        ; old cpu

        rsh r7, r1
        rsh r7, r7
        rsh r7, r7
        ldi r6, 256
        add r7, r6, r7
        lfp r7, r7          ; x 13 + 512
        rsh r6, r2
        rsh r6, r6
        rsh r6, r6
        add r7, r6, r7
        ldi r5, 3648        ; 512 + 3648 = 4160 -> collision level data matrix 
        add r7, r7, r5
        lfp r7, r7
        sub r0, r0, r7
        jif n .resolve_collision    ; total = 15 cycles

        ; new cpu

        ;sar 3, r7, r1
        ;add r7, r7, 256
        lfp r7, r7
        ;sar 3, r6, r2
        add r7, r6, r7
        ;add r7, r7, 3648
        lfp r7, r7
        sub r0, r0, r7
        jif n .resolve_collision    ; total = 9 cycles


