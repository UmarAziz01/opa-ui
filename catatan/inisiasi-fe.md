npm install @tanstack/react-query @tanstack/react-table axios lucide-react \
  @monaco-editor/react clsx tailwind-merge class-variance-authority \
  oidc-client-ts

npm install -D @types/node @types/react @types/react-dom

# 3. Inisialisasi shadcn/ui
npx shadcn@latest init -d

# 4. Pasang komponen dasar shadcn/ui yang diperlukan dashboard
npx shadcn@latest add button card dialog dropdown-menu input label \
  select table tabs badge sheet tooltip separator scroll-area alert