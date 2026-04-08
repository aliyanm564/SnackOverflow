# SnackOverflow — Next.js menu client

A Next.js front-end for browsing the SnackOverflow menu API: sign in, load a restaurant menu, search items, and filter by category or price.

## Prerequisites

- Node.js 20+ recommended
- SnackOverflow API running (for example `uvicorn backend.app.main:app --reload` on port 8000)

## Setup

```bash
cd frontend
npm install
```

Optional: copy `.env.example` to `.env.local` and adjust `NEXT_PUBLIC_API_BASE`.

## Development

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

The UI stores your JWT and API base URL in the browser (`localStorage`). You can still override the base URL in the **API connection** section.

## Production build

```bash
npm run build
npm start
```

## Stack

- [Next.js](https://nextjs.org) (App Router)
- TypeScript, Tailwind CSS v4
- [Lucide](https://lucide.dev) icons
