---
name: video-review
description: Open local project videos in the Codex right-side review panel, read frame annotations, and apply only the requested edits.
---

# Video review in Codex

For every user-reviewable video candidate, motion probe, or finished video produced in this task, provide its review interface with the actual video deliverable by default. Do not wait for the user to ask for annotation. Verify that the page displays the video and marking controls before describing it as a review interface.

When the user asks to mark a video, find the actual local video file first. Call `open_video_review` with the absolute `projectDir` and `filePath`. The video must be inside that project directory. Open the returned `reviewUrl` (the `/review/` page) in the current Codex task's right browser panel using `open_in_codex` with `placement:"right"`. Keep the conversation message compact; the full editor belongs in the side panel. Never open the raw `/video/` URL as the review interface: it is only the media stream and has no marking controls. `仅保存标注` only writes the mark file. `发送 N 条标注` sends the saved feedback to the task bound when the page opened. Its message contains each note's time, text, and approximate mark coordinates. The Codex queue path sends text only because the current CLI does not accept image attachments. A queued request alone does not prove the AI acted on it. Verify the destination task actually started processing before telling the user the edit request is underway.

When asked to edit from marks, call `get_video_review_notes` for that same file. Check the returned SHA-256 against the current candidate. Interpret each note's time and normalized mark coordinates against the corresponding video frame. Preserve shots and audio outside the requested scope. If an edit crosses a cut or requires a wider timing change, explain the exact scope before making it. Verify unmarked shots, ordering, timing, and audio in the result.

If a note contains `images`, open each saved reference image from `projectDir` plus its `relativePath` while reviewing that note. These pasted images are user feedback for the marked frame; they are not automatically verified product UI sources. The queue message carries local image paths as text because the Codex CLI queue does not accept image attachments.

Saved notes are review feedback. They are not approval of a candidate or authorization to change unrelated shots. Do not treat a screenshot or an old summary as the authoritative mark record.
