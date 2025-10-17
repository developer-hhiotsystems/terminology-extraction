# Glossary Management Frontend

React + TypeScript frontend for the Glossary Management System.

## Features

- **Glossary Management**: View, create, edit, and delete glossary entries
- **Search & Filter**: Full-text search with language and source filtering
- **PDF Upload**: Drag-and-drop PDF upload with automatic term extraction
- **Document Processing**: Configure NLP extraction options
- **Real-time Updates**: Instant feedback on all operations
- **Responsive Design**: Works on desktop and mobile devices

## Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **Axios** - HTTP client
- **React Router** - Client-side routing

## Prerequisites

- Node.js 16+ and npm
- Backend server running on http://localhost:8000

## Installation

```bash
cd src/frontend
npm install
```

## Development

```bash
npm run dev
```

The frontend will be available at http://localhost:3000

API requests are proxied to the backend at http://localhost:8000

## Build

```bash
npm run build
```

Built files will be in the `dist/` directory.

## Project Structure

```
src/frontend/
├── src/
│   ├── api/
│   │   └── client.ts          # API client for backend
│   ├── components/
│   │   ├── GlossaryList.tsx   # Glossary grid view
│   │   ├── GlossaryEntryForm.tsx  # Create/Edit form
│   │   ├── DocumentUpload.tsx     # PDF upload
│   │   └── DocumentList.tsx       # Document table
│   ├── types/
│   │   └── index.ts           # TypeScript types
│   ├── App.tsx                # Main app component
│   ├── App.css                # App styles
│   ├── index.css              # Global styles
│   └── main.tsx               # Entry point
├── index.html
├── package.json
├── tsconfig.json
├── vite.config.ts
└── README.md
```

## Features

### 1. Glossary List
- Grid view of all entries
- Search by term or definition
- Filter by language (EN/DE)
- Filter by source (Internal, NAMUR, DIN, etc.)
- View entry details
- Edit/Delete actions
- Validation status badges

### 2. Entry Form
- Create new entries manually
- Edit existing entries
- Required fields validation
- Source and language selection
- Domain tags (comma-separated)
- Validation status control

### 3. PDF Upload
- Drag-and-drop interface
- File type validation (.pdf only)
- File size validation (max 50MB)
- Upload progress feedback
- Processing options:
  - Extract terms (NLP)
  - Auto-validate
  - Language selection
  - Source classification
- Processing results display
- Terms extracted/saved count

### 4. Document Management
- Table view of uploaded documents
- Document status tracking
- Processing metadata
- Delete documents
- Terms extracted count

## API Integration

The frontend communicates with the backend API:

### Glossary Endpoints
- `GET /api/glossary` - List entries
- `POST /api/glossary` - Create entry
- `GET /api/glossary/{id}` - Get entry
- `PUT /api/glossary/{id}` - Update entry
- `DELETE /api/glossary/{id}` - Delete entry
- `GET /api/glossary/search?query=...` - Search

### Document Endpoints
- `POST /api/documents/upload` - Upload PDF
- `POST /api/documents/{id}/process` - Process PDF
- `GET /api/documents` - List documents
- `DELETE /api/documents/{id}` - Delete document

## Styling

The app uses a custom CSS design system with:
- CSS custom properties for theming
- Responsive grid layouts
- Card-based UI components
- Status-based color coding
- Smooth animations

### Color Scheme
- Primary: Blue (#2563eb)
- Success: Green (#10b981)
- Warning: Yellow (#f59e0b)
- Danger: Red (#ef4444)
- Neutral: Gray shades

## Development Notes

### API Proxy
The Vite dev server proxies `/api` requests to the backend:
```typescript
// vite.config.ts
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

### Type Safety
All API responses are typed with TypeScript interfaces in `src/types/index.ts`

### Error Handling
- API errors displayed to user
- Form validation feedback
- Loading states
- Empty states

## Future Enhancements

- [ ] Dark mode support
- [ ] Advanced filtering options
- [ ] Bulk operations
- [ ] Export glossary (CSV, JSON)
- [ ] Term relationship visualization
- [ ] Real-time collaboration
- [ ] Progressive Web App (PWA)
- [ ] Internationalization (i18n)

## Troubleshooting

### Backend Connection Error
Make sure the backend server is running:
```bash
python src/backend/app.py
```

### TypeScript Errors
Clean install dependencies:
```bash
rm -rf node_modules package-lock.json
npm install
```

### Build Errors
Check TypeScript configuration:
```bash
npm run typecheck
```

## License

Part of the Glossary Management System project.
