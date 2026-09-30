import re

filepath = '/home/sece2026-student07/legalai-finetuning/src/api/supabase_case_service.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update CREATE TABLE IF NOT EXISTS conversations
if 'messages TEXT' not in content:
    content = content.replace(
        'contextSettings TEXT,\n            updatedAt TEXT NOT NULL\n        )',
        'contextSettings TEXT,\n            updatedAt TEXT NOT NULL,\n            messages TEXT\n        )'
    )
    alter_clause = '        try:\n            cur.execute("ALTER TABLE conversations ADD COLUMN messages TEXT")\n        except Exception:\n            pass\n'
    if 'ALTER TABLE conversations ADD COLUMN messages TEXT' not in content:
        content = content.replace(
            '# Case Chat Memory table',
            alter_clause + '\n        # Case Chat Memory table'
        )

# 2. Update get_all_conversations
old_select = 'SELECT id, title, mode, caseId, caseNumber, selectedCases, contextSettings, updatedAt FROM conversations ORDER BY updatedAt DESC'
new_select = 'SELECT id, title, mode, caseId, caseNumber, selectedCases, contextSettings, updatedAt, messages FROM conversations ORDER BY updatedAt DESC'
content = content.replace(old_select, new_select)

old_loop = '''            cid, title, mode, caseId, caseNumber, selectedCases_json, contextSettings_json, updatedAt = r
            selectedCases = []
            if selectedCases_json:
                try:
                    selectedCases = json.loads(selectedCases_json)
                except Exception:
                    pass
            contextSettings = {}
            if contextSettings_json:
                try:
                    contextSettings = json.loads(contextSettings_json)
                except Exception:
                    pass

            cur.execute("""
                SELECT id, role, content, intent, timestamp FROM case_chat_memory
                WHERE conversation_id = ?
                ORDER BY id ASC
            """, (cid,))
            msg_rows = cur.fetchall()
            messages = []
            for m in msg_rows:
                messages.append({
                    "id": f"msg-{m[0]}",
                    "role": m[1],
                    "content": m[2],
                    "query_type": m[3],
                    "timestamp": m[4],
                    "reliability": "supported",
                    "reliabilityLabel": "Stored in Database"
                })'''

new_loop = '''            cid, title, mode, caseId, caseNumber, selectedCases_json, contextSettings_json, updatedAt, messages_json = r
            selectedCases = []
            if selectedCases_json:
                try:
                    selectedCases = json.loads(selectedCases_json)
                except Exception:
                    pass
            contextSettings = {}
            if contextSettings_json:
                try:
                    contextSettings = json.loads(contextSettings_json)
                except Exception:
                    pass

            messages = []
            if messages_json:
                try:
                    messages = json.loads(messages_json)
                except Exception:
                    pass

            if not messages:
                cur.execute("""
                    SELECT id, role, content, intent, timestamp FROM case_chat_memory
                    WHERE conversation_id = ?
                    ORDER BY id ASC
                """, (cid,))
                msg_rows = cur.fetchall()
                for m in msg_rows:
                    messages.append({
                        "id": f"msg-{m[0]}",
                        "role": m[1],
                        "content": m[2],
                        "query_type": m[3],
                        "timestamp": m[4],
                        "reliability": "supported",
                        "reliabilityLabel": "Stored in Database"
                    })'''

content = content.replace(old_loop, new_loop)

# 3. Update save_conversation
old_save = '''        updatedAt = conv.get("updatedAt", time.strftime("%Y-%m-%d %H:%M:%S"))

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO conversations (id, title, mode, caseId, caseNumber, selectedCases, contextSettings, updatedAt)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                mode = excluded.mode,
                caseId = excluded.caseId,
                caseNumber = excluded.caseNumber,
                selectedCases = excluded.selectedCases,
                contextSettings = excluded.contextSettings,
                updatedAt = excluded.updatedAt
        """, (cid, title, mode, caseId, caseNumber, selectedCases, contextSettings, updatedAt))'''

new_save = '''        updatedAt = conv.get("updatedAt", time.strftime("%Y-%m-%d %H:%M:%S"))
        messages_json = json.dumps(conv.get("messages", []))

        conn = sqlite3.connect(self.db_path)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO conversations (id, title, mode, caseId, caseNumber, selectedCases, contextSettings, updatedAt, messages)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                mode = excluded.mode,
                caseId = excluded.caseId,
                caseNumber = excluded.caseNumber,
                selectedCases = excluded.selectedCases,
                contextSettings = excluded.contextSettings,
                updatedAt = excluded.updatedAt,
                messages = excluded.messages
        """, (cid, title, mode, caseId, caseNumber, selectedCases, contextSettings, updatedAt, messages_json))'''

content = content.replace(old_save, new_save)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated supabase_case_service.py")
