---
title: Feedback
---

Add feedback on chat messages and executions.

Create/list/get/update/delete:
```python
fb = client.feedback.create(
    project_id=project.id,
    chat_message_id="msg-123",
    feedback="Great SQL!",
    is_positive=True,
)

items = client.feedback.list(project.id)
one = client.feedback.get(project.id, fb.id)

updated = client.feedback.update(project.id, fb.id, feedback="Updated feedback", is_positive=True)
client.feedback.delete(project.id, fb.id)
```

Helpers:
```python
pos = client.feedback.list_positive(project.id)
neg = client.feedback.list_negative(project.id)
msg_fbs = client.feedback.get_feedback_for_message(project.id, "msg-123")

# Shortcuts
fb_pos = client.feedback.create_positive(project.id, "msg-123", "Perfect!")
fb_neg = client.feedback.create_negative(project.id, "msg-456", "Incorrect results")
```
