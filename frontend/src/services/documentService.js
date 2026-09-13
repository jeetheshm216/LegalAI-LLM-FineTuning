import { INITIAL_DOCUMENTS } from '../mock/mockDocuments';

let documentsStore = [...INITIAL_DOCUMENTS];

export const documentService = {
  getAllDocuments: async () => {
    return [...documentsStore];
  },

  getDocumentsByCase: async (caseId) => {
    return documentsStore.filter(d => d.caseId === caseId);
  },

  getDocumentById: async (docId) => {
    return documentsStore.find(d => d.id === docId) || null;
  },

  uploadDocument: async ({ caseId, caseNumber, file, category }) => {
    const newDoc = {
      id: `doc-${Date.now()}`,
      caseId,
      caseNumber: caseNumber || "2024-CV-1187",
      filename: file.name,
      category: category || "Evidence",
      fileType: file.name.endsWith('.docx') ? 'docx' : 'pdf',
      fileSize: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      uploadedDate: new Date().toISOString().split('T')[0],
      status: "processing",
      statusLabel: "Processing",
      pages: Math.floor(4 + Math.random() * 20),
      excerpt: "Document received and pending OCR indexing for legal citation synthesis."
    };

    documentsStore = [newDoc, ...documentsStore];
    return newDoc;
  },

  retryDocument: async (docId) => {
    documentsStore = documentsStore.map(d => {
      if (d.id === docId) {
        return {
          ...d,
          status: "processing",
          statusLabel: "Processing"
        };
      }
      return d;
    });
    return documentsStore.find(d => d.id === docId);
  }
};
