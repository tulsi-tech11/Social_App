import os
import re

base_dir = r"d:\25september\Django\velora_env_final\velora_env_final\velora_env\velora_env\velora\myapp\templates\myapp"

script_content = """
<script>
  // Fetch dynamic badge counts
  document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/unread-counts/', { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
      .then(res => res.json())
      .then(data => {
        const msgBadge = document.getElementById('msg-badge');
        const notifBadge = document.getElementById('notif-badge');
        
        if (msgBadge) {
          if (data.messages > 0) {
            msgBadge.textContent = data.messages;
            msgBadge.style.display = 'flex';
          } else {
            msgBadge.style.display = 'none';
          }
        }
        
        if (notifBadge) {
          if (data.notifications > 0) {
            notifBadge.textContent = data.notifications;
            notifBadge.style.display = 'flex';
          } else {
            notifBadge.style.display = 'none';
          }
        }
      })
      .catch(err => console.error('Error fetching badge counts:', err));
  });
</script>
</body>
"""

for filename in os.listdir(base_dir):
    if not filename.endswith('.html'): continue
    filepath = os.path.join(base_dir, filename)
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip if already has msg-badge
    if 'id="msg-badge"' in content: continue

    # Replace badge strings
    content = re.sub(r'<span\s+class="badge">\d+</span>', '<span class="badge" id="msg-badge" style="display:none;"></span>', content)
    content = re.sub(r'<span\s+class="badge\s+red">\d+</span>', '<span class="badge red" id="notif-badge" style="display:none;"></span>', content)

    # Append script before </body>
    if '</body>' in content:
        content = content.replace('</body>', script_content)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

print("Updated badges in all templates.")
