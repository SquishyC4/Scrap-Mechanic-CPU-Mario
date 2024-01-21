; Mario Code implemented in the new CPU's assembly

#include 


; variables
#define 
    player_x_vel,  [4096]    ; pixels/s
    player_y_vel,  [4097]    ; pixels/s
    grouded,       [4098]    ; 1 = grounded, 0 = not grounded
    wall_x_blocks, [4099]
    wall_y_blocks, [4100]
    wall_x_pixels, [4101]
    wall_y_pixels, [4102]
    prev_player_x, [4103]    ; physics. collision detection
    prev_player_y, [4104]
    curr_player_x, [4105]
    curr_player_x, [4106]

; register names
#define
    mxl, r30
    mxh, r31


Main:
    call Render_Scene


Render_Scene:
    mov r1, 0b0100000000000101    ; setup gpu instruction
                                  ; all blocks can assume 40 pixels
    pst p1, r1
    mov r1, wall_x_blocks    ; loop i vaiable
    add r2, r1, 12           ; max i value
    lod r3, wall_y_blocks
    add r4, r3, 8            ; max j
.L5
    add r6, r1, 256
    lfp r6, r6               ; x13 + 512 --> start of list in render 2x2 matrix
    lfp r5, r6               ; number of blocks t orender
    add r6, r6, 1
    add r3, r5, r6           ; max value of pointer
    jmp .L2
.L4
    lfp r7, r6                   ; load block data. first 4 bits are the y coord (in blocks)
    and r8, r7, 15               ; extract y coord
    sub r31, r8, r4              ; check if its greater then y limit
    jif neg, .L1                 ; break from inner loop    
    sub r31, r8, wall_y_blocks   ; check if its less than base height
    jif pos, .L3                 ; skip draw
    jmp .call_gpu
.L3
    add r6, r6, r1
    sub r31, r3, r6
    jif pos, .L4
    add r1, r1, 1
    sub r31, r1, r2
    jif neg, .L5
    jmp .update_screen
.call_gpu
    sub r7, r7, r1        ; extract block id and store to port for gpu
    pst p2, r7
    sal 3, r10, r8
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

