# Brief: add the Camera column to a shots.md (rule 10)

Read `history-indio/pipeline/CAMERA.md` in full first; it is the law here. Then, for each `shots.md` you are given
(read that episode's `script_multispeaker.txt` too, to know what each line is doing), edit ONLY the shot table and
add one note line; change nothing else in the file, and no other file.

1. Keep the `#` and `Sent.` columns exactly as they are (same rows, same order, same numbers).
2. Rename the last column to `Camera` (it may now be called "Framing and move" or similar) and rewrite each cell as
   `size / angle / move / reason`, e.g. `close-up / low angle / dolly_in / he threatens her`.
   - size: extreme wide, wide, medium, medium close-up, close-up, extreme close-up, insert, two-shot, over-the-shoulder.
   - angle: eye level, low angle, high angle, bird's-eye, Dutch tilt, from behind.
   - move: only names CAMERA.md uses: hold, push_in, pull_out, dolly_in, crane_down, crane_up, orbit_left, orbit_right,
     pan_left, pan_right, tilt_up, tilt_down, rack_focus. "hold" when no five-word reason exists.
   - reason: five words or fewer, plain English.
   - after the reason, only where the table calls for it, add `; fx: punch` / `; fx: shake, impact`, `; dof: far`,
     and `; in: dissolve|whip|flash` for the transition INTO the shot. No mention means a plain cut. Dissolve only when
     time or place changes, whip only inside action, flash only on the time jump or a memory.
   - a reveal says where it ends: `... / tilt_up / ends on the sign`.
3. Choose by what the line is doing (table 1 of CAMERA.md), never by rotation. Obey section 2: the size changes at
   every cut (never two neighbouring rows with the same size and angle on the same person); pan direction carries
   over; people keep their side of the frame in a conversation; depth moves only where the still has a near subject
   and a far background.
4. Big moves are rare: mark exactly TWO or THREE rows per episode as the high points, by starting the Camera cell
   with `**HIGH POINT** `; only those rows (plus, if it truly fits, the establishing shot of a new place with
   crane_down) may use orbit, crane or dolly. Usual high points: the fall, the comeback, the hero's line or the last
   reveal. Every other row is a small push_in, a pan/tilt with a reason, a pull_out, or a hold.
5. Rewrite the start of each "What we see" cell so that the size and angle come first in plain words ("Low-angle
   close-up of...", "Bird's-eye wide view of...", "Over Sepa's shoulder, we see..."), keeping every picture detail
   already there (labels such as "Hook:", "Today:" may stay in front). Do not invent new picture content, do not
   remove any, and keep the notes about text added in code.
6. Directly above the table add one line: `Camera (rule 10): column follows pipeline/CAMERA.md; rows marked HIGH POINT are the only big moves.`
7. Keep the table valid Markdown (same number of cells in every row; no `|` inside a cell). Do not commit or push.

Report back in three lines per episode: the rows marked HIGH POINT and why, how many rows hold still, and anything
you could not fit to the table.
