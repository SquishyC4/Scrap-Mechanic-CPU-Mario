; Mario Code implemented in the new CPU's assembly

#include test.txt


; variables
#define 
    player_x_vel,  [4096]    ; pixels/s
    player_y_vel,  [4097]    ; pixels/s
    grounded,       [4098]    ; 1 = grounded, 0 = not grounded
    wall_x_blocks, [4099]
    wall_y_blocks, [4100]
    wall_x_pixels, [4101]
    wall_y_pixels, [4102]
    prev_player_x, [4103]    ; physics. collision detection
    prev_player_y, [4104]
    curr_player_x, [4105]
    curr_player_y, [4106]
#end

; register names
; mainly for when using imul to prevent confusion
#define
    mxl, r30
    mxh, r31
#end

Main:
    cad grounded, r0, r0    ; set grounded
    call Input
    call Render_Scene

Input:
    pld r5, p4            ; load input
    mov r1, player_x_vel
    mov r2, player_y_vel
    and r6, r6, 1
    xor r31, r6, 1
    jif z, .left
.test_right
    and r6, r6, 2
    xor r31, r6, 2
    jif z, .right
.test_jump
    and r6, r5, 4
    xor r31, r6, 4
    jif z, .jump
    jmp .physics

.left
    sub r1, r1, 1
    jif pos, .test_right
    sub r31, r1, 0b1111111111110111    ; -8
    jif pos, .test_right
    sub player_x_vel, r1, r31              ; x_vel less than -8 so set to -8
    jmp .test_right
.right
    add r1, r1, 1
    sub r31, r1, 8
    jif neg, .test_jump
    sub player_x_vel, r1, r31
    jmp .test_jump
.jump
    mov r31, grounded
    and r31, r31, 1
    jif z, .physics
    mov r31, 8
    mov player_y_vel, r31
    mov grounded, r0

.physics
    and r31, r5, 3
    jif z, .friction
.?gravity
    mov r31, grounded
    and r31, r31, 1
    jif z .gravity
    jmp .update

.friction
    and r1, r1, r1
    jif z, .?gravity

    ; bit twiddling magic
    ; might actually be slower than cond jumps

    cwd r31, r1
    xor r1, r1, r31
    sub r1, r1, 1
    xor r1, r1, r31
    mov player_x_vel, r1
    jmp .?gravity

.gravity
    and r2, r2, r2
    jif pos, .update
    sub r31, r2, 0b1111111111110111    ; -8
    jif pos, .update
    sub player_y_vel, r2, r31

.update
    mov r3, curr_player_x    ; mov current positions to previous for collision calculations
    mov r4, curr_player_y    
    mov prev_player_x, r3
    mov prev_player_y, r4
    add r1, r3, r1    ; update and store the current positions
    add r2, r4, r2
    mov curr_player_x, r1
    mov curr_player_y, r2

Collision:
.detect_collision                ; starting at the bottom left corner, go over all corners,
                                 ; get block from corner position
                                 ; if there is a block, resolve the collision
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7                   ; x13 + 512
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    jif neg .resolve_collision

    add r1, r1, 6               ; bottom right corner

    sar 3, r7, r1               ; exact same deal
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    jif neg .resolve_collision

    add r2, r2, 7               ; top right corner

    sar 3, r7, r1               ; exact same deal
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    jif neg .resolve_collision

    sub r1, r1, 6               ; top left corner

    sar 3, r7, r1               ; exact same deal
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    jif neg .resolve_collision

    ; no collision so check if the player has crossed the wall boundry
    jmp Wall

.resolve_collision        ; tbh i cant remember how this works exactly, but it does
    ; r1 has player corner x
    ; r2 has player corer y
    ; r10 = player_x previous
    ; r11 = player_y previous
    ; r12 = block_x
    ; r13 = block_y
    ; r14 = x_vel
    ; r15 = y_vel

    mov r10, prev_player_x
    mov r11, prev_player_y
    mov r12, curr_player_x        ; block x
    mov r13, curr_player_y        ; block y
    and r12, r12, 0b1111111111111000
    and r13, r13, 011111111111111000
    mov r14, player_x_vel
    mov r15, player_y_vel

    sub r0, r0, r14
    jif neg, .+x
    sub r0, r0, r15
    jif neg, .-x+y
    add r12, r12, 7
    add r13, r13, 7

    sub r20, r13, r10
    imul r20, r14
    mov r11, mxl
    sub r21, r3, r11
    imul r21, r15
    sub r7, r11, mxl

    jif neg .--side

    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    
    jif neg .resolve_x
    mov r31, 1
    mov grounded, r31
    jmp .resolve_y

.--side
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    
    jif z, .resolve_x
    mov r31, 1
    mov grounded, r31
    jmp .resolve_y

.-x+y
    add r12, r12, 7
    
    sub r20, r13, r10
    imul r20, r14
    mov r11, mxl
    sub r21, r3, r11
    imul r21, r15
    sub r7, r11, mxl

    jif neg .-+bottom
    
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    
    jif z, .resolve_x
    jmp .resolve_y

.-+bottom
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    
    jif z, .resolve_x
    jmp .resolve_y

.+x
    sub r0, r0, r15
    jif neg, .+x+y
.+x-y
    add r13, r13, 7

    sub r20, r13, r10
    imul r20, r14
    mov r11, mxl
    sub r21, r3, r11
    imul r21, r15
    sub r7, r11, mxl

    jif neg, .+-top

    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7

    jif z, .resolve_x
    mov r31, 1
    mov grounded, r31
    jmp .resolve_y

.+-top
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7

    jif neg, .resolve_x
    mov r31, 1
    mov grounded, r31
    jmp .resolve_y

.+x+y
    sub r20, r13, r10
    imul r20, r14
    mov r11, mxl
    sub r21, r3, r11
    imul r21, r15
    sub r7, r11, mxl

    jif neg, .++side
    
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    jif neg, .resolve_x
    jmp .resolve_y

.++side
    sar 3, r7, r1
    add r7, r7, 256
    lfp r7, r7
    sar 3, r6, r2
    add r7, r6, r7
    add r7, r7, 3648
    lfp r7, r7
    sub r0, r0, r7
    jif z, .resolve_x
    jmp .resolve_y
    
.resolve_x
    sub r31, r12, r1
    add r31, curr_player_x, r31
    mov curr_player_x, r31
    mov player_x_vel, r0
    jmp Wall

.resolve_y
    sub r31, r13, r2
    add r31, curr_player_y, r31
    mov curr_player_y, r31
    mov player_y_vel, r0
    jmp Wall

Wall:
    mov r1, curr_player_x
    mov r2, wall_x_pixels
    sub r0, r1, r2
    jif neg, .left_wall
    add r3, r2, 33
    sub r0, r3, r1
    jif neg, .updt_wall
    jmp Render_Scene
.left_wall
    cad curr_player_x, r2, r0
    jmp .wall_block_updt
.updt_wall
    sub r2, r3, r1
    add r2, r2, r4
    mov wall_x_pixels, r2

.wall_block_updt
    sar 3, r2, r2
    mov wall_x_blocks, r2
    mov r3, curr_player_y
    sar 3, r3, r3
    mov wall_y_blocks, r3
    jmp Render_Scene

Render_Scene:
    mov r1, 0b0100000000000101   ; setup gpu instruction
                                 ; all blocks can assume 40 pixels
    pst p1, r1
    mov r1, wall_x_blocks        ; loop i vaiable
    add r2, r1, 12               ; max i value
    lod r3, wall_y_blocks
    add r4, r3, 8                ; max j
.L5
    add r6, r1, 256
    lfp r6, r6                   ; x13 + 512 --> start of list in render 2x2 matrix
    lfp r5, r6                   ; number of blocks t orender
    add r6, r6, 1
    add r3, r5, r6               ; max value of pointer
    jmp .L2
.L4
    lfp r7, r6                   ; load block data. first 4 bits are the y coord (in blocks)
    and r8, r7, 15               ; extract y coord
    sub r31, r8, r4              ; check if its greater then y limit
    jif neg, .L1                 ; break from inner loop    
    sub r31, r8, wall_y_blocks   ; check if its less than base height
    jif neg, .L3                 ; skip draw
    jmp .call_gpu
.L3
    add r6, r6, r1
.L2
    sub r31, r3, r6
    jif pos, .L4
.L1
    add r1, r1, 1
.L0    
    sub r31, r1, r2
    jif neg, .L5
    jmp .update_screen
.call_gpu
    sub r7, r7, r1               ; extract block id and store to port for gpu
    pst p2, r7
    sal 3, r10, r8               ; compute block position on screen
    sub r10, r10, wall_y_pixels
    sal 3, r11, r1
    sub r11, r11, wall_x_pixels
    sal 8, r12, r11
    cad r13, r11, r12
    pst p3, r13
    jmp .L3
.update_screen
    mov r31, 0b1000000000000000
    pst p1, r3
    mov r31, 0b1100000000000000
    pst p1, r3
    ret
