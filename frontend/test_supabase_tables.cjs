const { createClient } = require('@supabase/supabase-js');
const sb = createClient('https://brveublsqvbulxxkgjxu.supabase.co', 'sb_publishable_fo2AZ4LYA90V1N2ghE4JHw_qSTCGfix');

async function test() {
  const tables = ['cases', 'documents', 'case_documents', 'conversations', 'messages', 'chat_history', 'case_chat_memory', 'advocates'];
  for (const table of tables) {
    try {
      const { data, error } = await sb.from(table).select('*').limit(2);
      if (error) {
        console.log(`Table '${table}': ERROR -> ${error.message} (code: ${error.code})`);
      } else {
        console.log(`Table '${table}': SUCCESS -> ${data.length} records. Sample keys: ${data.length > 0 ? Object.keys(data[0]).join(', ') : 'none'}`);
      }
    } catch (e) {
      console.log(`Table '${table}': EXCEPTION -> ${e.message}`);
    }
  }
}
test();
