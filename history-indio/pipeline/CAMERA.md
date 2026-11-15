# Camera: which shot, which move, and why

The owner's rule: use the whole film vocabulary (pan, dolly, zoom, reveal, tilt, drone, centring on the subject),
but only where it serves the scene. A move that does not match what is happening is a fault, the same as a bad still.

A shot has two parts. The **angle and size** are drawn into the still (`key_prompts.json`). The **move** is added by the
builder (`shots_fx.json`, `"move"`). Choose both from what the line is doing, never from a rotation.

## 1. What the line is doing decides the shot
| The line is... | Angle and size in the still | Move | Cut into it with |
|---|---|---|---|
| Opening a new place or time | wide, high angle or bird's-eye (the "drone" view), people small | `crane_down` or slow `push_in` | `dissolve` |
| Someone speaking plainly | medium or medium close-up, eye level, speaker off-centre, looking into the empty side | slow `push_in` (small) | `cut` |
| Two people talking | over-the-shoulder, alternate sides, keep each on their own side of the frame | none or small `push_in` | `cut` |
| A threat or a shout | close-up, low angle on the one who threatens; high angle on the one threatened | `dolly_in` + `"fx": ["punch"]` | `cut` |
| A blow, a fall, a crash | close, Dutch tilt allowed | `"fx": ["shake","impact"]`, no slow move | `cut` or `whip` |
| Fear, being watched | wide with the person small, or from behind an object in the foreground | `orbit_left`/`orbit_right`, slow | `cut` |
| A reveal (a face, a sign, who was hidden) | draw the still so the surprise is at one edge or the top | `tilt_up`, `pan_*` or `pull_out` that ENDS on the surprise | `cut` |
| A hero's entrance or his line | low angle, subject dead centre, light behind | `dolly_in`; hold still on the words | `cut`, after a hush |
| A tender moment | close two-shot, shallow depth, `"dof": "far"` | very slow `push_in` or `rack_focus` | `dissolve` |
| An object that matters (medallion, paper, sign) | extreme close-up, object centred | `rack_focus` or small `push_in` | `cut` |
| A crowd answering | wide, from behind the crowd or from above | `crane_up` or `pull_out` | `cut` |
| Chase, running | side view or from behind, room in front of the runner | `pan_*` in the direction of travel | `whip` |
| Time passing, a memory | wide or detail, soft light | `pull_out`, slow | `dissolve` |
| The last picture of a scene | whatever the scene ends on | `pull_out` or hold | `dissolve` or `flash` only for the time jump |

## 2. Rules that keep it from looking like a machine made it
1. **Motivated or still.** If you cannot say in five words why the camera moves ("to show the sign", "he steps closer"),
   the shot holds still with only a 2-3% drift.
2. **Direction carries over.** A pan follows the look or the travel. Do not pan right in one shot and left in the next
   on the same action. People keep their side of the frame through a conversation (the 180-degree rule).
3. **Change the size at every cut.** Wide to close or close to wide; never two shots of the same size and angle in a row
   on the same person (that is a jump cut).
4. **Speed follows the feeling.** Slow for dread, grief, tenderness; fast only for action. One fast move per scene at most.
5. **Big moves are rare.** `orbit`, `crane`, `dolly` at most once or twice a scene, kept for the high points.
   Punch-in and shake only on a shout or a blow.
6. **Transitions are plain cuts by default.** `whip` only inside action, `dissolve` only for time or place changing,
   `flash` only for the time jump or a memory, `slash` only on a blade. Set `"trans"` per shot; do not let the builder
   rotate through its list.
7. **The reveal ends on the surprise and stops there** for at least half a second before the next cut.
8. **Subject in the right place.** Centre only for power or confrontation; otherwise on a third, with room in the
   direction of the look. Check that subtitles (at about 63% of the height) do not cover the face or the thing revealed.
9. **Depth moves need depth.** `dolly`, `orbit`, `crane`, `rack_focus` only on stills with a clear near subject and a far
   background; on flat stills use `push_in`, `pan`, `tilt`.
10. **Look at it moving.** After the build, watch each move at full speed. A move that tears the picture, slides a face
    off the frame, or zooms into a blur is replaced by a hold.

## 3. In the files
- `key_prompts.json`: put the size and angle first in `subject`, in plain words ("Low-angle close-up of...",
  "Bird's-eye wide view of...", "Over the shoulder of X, we see...").
- `shots_fx.json`: `"move"`, optional `"fx"`, `"dof"`, `"focus_to"`, `"trans"`; add `"why": "..."` with the five-word
  reason. A shot with no reason gets no move.
- `shots.md`: one extra column, "Camera", with size / angle / move / reason, so the plan can be read before anything is drawn.
- Transitions in `shots_fx.json`: `"_": {"trans_default": "cut"}` makes every cut plain unless a line says otherwise;
  a line's own `"trans_in": "dissolve" | "whip" | "flash" | "slash" | "zoom" | "cut"` sets the way INTO that line.
  Without `trans_default` the builder still rotates through its list (old episodes are unchanged).
