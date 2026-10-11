import argparse
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
from time import perf_counter
from servico import Acervo
from algoritmos import ordenar

class App:
    def __init__(self, root, service):
        self.root, self.service = root, service
        root.title('Acervo | Grupo 26'); root.geometry('1180x760'); root.minsize(960, 650)
        style = ttk.Style(); style.theme_use('clam')
        style.configure('Treeview', rowheight=29, font=('Segoe UI', 10))
        style.configure('TButton', padding=7); style.configure('TLabel', font=('Segoe UI', 10))
        ttk.Label(root, text='Acervo bibliográfico', font=('Segoe UI', 23, 'bold')).pack(anchor='w', padx=22, pady=(18, 3))
        ttk.Label(root, text='Leitores, circulação e laboratório de ordenação').pack(anchor='w', padx=22, pady=(0, 14))
        tabs = ttk.Notebook(root); tabs.pack(fill='both', expand=True, padx=20, pady=5)
        self.books = ttk.Frame(tabs, padding=14); self.readers = ttk.Frame(tabs, padding=14); self.loans = ttk.Frame(tabs, padding=14)
        for frame, name in [(self.books,'Acervo e ordenação'),(self.readers,'Leitores'),(self.loans,'Empréstimos e devoluções')]: tabs.add(frame,text=name)
        self.status = tk.StringVar(value='Pronto. Os dados são salvos automaticamente.')
        ttk.Label(root, textvariable=self.status).pack(anchor='w', padx=22, pady=12)
        self.build_books(); self.build_readers(); self.build_loans(); self.refresh()

    def fields(self, parent, names):
        frame = ttk.Frame(parent); frame.pack(fill='x', pady=8)
        values = {}
        for i, name in enumerate(names):
            ttk.Label(frame,text=name).grid(row=0,column=i,sticky='w',padx=4)
            var = tk.StringVar(); ttk.Entry(frame,textvariable=var,width=18).grid(row=1,column=i,sticky='ew',padx=4)
            frame.columnconfigure(i,weight=1); values[name]=var
        return values

    def tree(self,parent,columns):
        frame=ttk.Frame(parent); frame.pack(fill='both',expand=True,pady=10)
        tree=ttk.Treeview(frame,columns=columns,show='headings',selectmode='browse')
        for col in columns: tree.heading(col,text=col); tree.column(col,width=100,minwidth=45)
        scroll=ttk.Scrollbar(frame,orient='vertical',command=tree.yview); tree.configure(yscrollcommand=scroll.set)
        tree.pack(side='left',fill='both',expand=True); scroll.pack(side='right',fill='y')
        return tree

    def act(self, callback):
        try:
            callback(); self.refresh(); self.status.set('Operação concluída e salva.')
        except (ValueError, OSError) as exc: messagebox.showerror('Não foi possível concluir',str(exc),parent=self.root)

    def build_books(self):
        ttk.Label(self.books,text='Cadastre livros e explore os critérios de ordenação do acervo.').pack(anchor='w')
        self.bvars=self.fields(self.books,['Título','Autor','Gênero','Ano','Exemplares'])
        ttk.Button(self.books,text='Cadastrar livro',command=lambda:self.act(self.save_book)).pack(anchor='w')
        controls=ttk.Frame(self.books); controls.pack(fill='x',pady=12)
        self.algorithm=tk.StringVar(value='Heap Sort'); self.field=tk.StringVar(value='nota_media'); self.direction=tk.StringVar(value='Decrescente')
        for var, values in [(self.algorithm,['Heap Sort','Merge Sort']),(self.field,['titulo','autor','genero','ano','id','disponiveis','popularidade','nota_media']),(self.direction,['Crescente','Decrescente'])]:
            ttk.Combobox(controls,textvariable=var,values=values,state='readonly',width=19).pack(side='left',padx=(0,8))
        ttk.Button(controls,text='Ordenar',command=self.refresh_books).pack(side='left')
        self.booktree=self.tree(self.books,['ID','Título','Autor','Ano','Disponíveis','Empréstimos','Nota média'])
        self.metrics=tk.StringVar(); ttk.Label(self.books,textvariable=self.metrics).pack(anchor='w')
        ttk.Label(self.books,text='Sem avaliação aparece ao final em ambos os sentidos. Merge Sort preserva a ordem dos empates.').pack(anchor='w',pady=8)

    def save_book(self):
        self.service.livro(*(self.bvars[n].get() for n in ['Título','Autor','Gênero','Ano','Exemplares']))
        for var in self.bvars.values(): var.set('')

    def build_readers(self):
        self.edit_id=None
        self.rvars=self.fields(self.readers,['Nome','Matrícula','Contato'])
        buttons=ttk.Frame(self.readers); buttons.pack(fill='x')
        ttk.Button(buttons,text='Salvar leitor',command=lambda:self.act(self.save_reader)).pack(side='left')
        ttk.Button(buttons,text='Editar selecionado',command=lambda:self.act(self.edit_reader)).pack(side='left',padx=8)
        ttk.Button(buttons,text='Novo / limpar',command=self.clear_reader).pack(side='left')
        self.readertree=self.tree(self.readers,['ID','Nome','Matrícula','Contato'])

    def clear_reader(self):
        self.edit_id=None
        for var in self.rvars.values(): var.set('')

    def save_reader(self):
        self.service.leitor(*(self.rvars[n].get() for n in ['Nome','Matrícula','Contato']), id=self.edit_id)
        self.clear_reader()

    def selected(self,tree):
        selection=tree.selection()
        if not selection: raise ValueError('Selecione uma linha na tabela.')
        return int(selection[0])

    def edit_reader(self):
        self.edit_id=self.selected(self.readertree)
        row=self.service._get(self.service.dados['leitores'],self.edit_id)
        for label,key in [('Nome','nome'),('Matrícula','matricula'),('Contato','contato')]: self.rvars[label].set(row[key])

    def build_loans(self):
        form=ttk.Frame(self.loans); form.pack(fill='x')
        ttk.Label(form,text='Leitor').grid(row=0,column=0,sticky='w')
        ttk.Label(form,text='Livro').grid(row=0,column=1,sticky='w')
        self.readerbox=ttk.Combobox(form,state='readonly',width=35); self.readerbox.grid(row=1,column=0,padx=(0,10))
        self.bookbox=ttk.Combobox(form,state='readonly',width=42); self.bookbox.grid(row=1,column=1,padx=(0,10))
        ttk.Button(form,text='Emprestar por 14 dias',command=lambda:self.act(self.borrow)).grid(row=1,column=2)
        ttk.Label(self.loans,text='Selecione um empréstimo abaixo para registrar a devolução.').pack(anchor='w',pady=(20,5))
        returns=ttk.Frame(self.loans); returns.pack(fill='x')
        ttk.Label(returns,text='Nota de 0 a 5 (opcional):').pack(side='left')
        self.rating=tk.StringVar(); ttk.Entry(returns,textvariable=self.rating,width=8).pack(side='left',padx=8)
        ttk.Button(returns,text='Devolver selecionado',command=lambda:self.act(self.return_book)).pack(side='left')
        self.loantree=self.tree(self.loans,['ID','Leitor','Livro','Empréstimo','Prazo','Situação','Nota'])

    def borrow(self):
        if self.readerbox.current()<0 or self.bookbox.current()<0: raise ValueError('Selecione leitor e livro.')
        self.service.emprestar(self.reader_ids[self.readerbox.current()],self.book_ids[self.bookbox.current()])

    def return_book(self):
        nota=self.rating.get().strip().replace(',','.')
        self.service.devolver(self.selected(self.loantree),nota if nota else None); self.rating.set('')

    def fill(self,tree,rows):
        tree.delete(*tree.get_children())
        for id,values in rows: tree.insert('', 'end', iid=str(id), values=values)

    def refresh_books(self):
        start=perf_counter()
        books=ordenar(self.service.livros(),self.field.get(),self.direction.get()=='Crescente',self.algorithm.get())
        elapsed=(perf_counter()-start)*1000
        self.fill(self.booktree,[(b['id'],(b['id'],b['titulo'],b['autor'],b['ano'],b['disponiveis'],b['popularidade'],'Sem nota' if b['nota_media'] is None else f"{b['nota_media']:.2f}")) for b in books])
        self.metrics.set(f'{self.algorithm.get()} | {len(books)} livros | preparação e ordenação: {elapsed:.3f} ms')

    def refresh(self):
        self.refresh_books()
        readers=self.service.dados['leitores']; books=self.service.livros()
        self.fill(self.readertree,[(r['id'],(r['id'],r['nome'],r['matricula'],r['contato'])) for r in readers])
        self.reader_ids=[r['id'] for r in readers]; self.book_ids=[b['id'] for b in books]
        self.readerbox['values']=[f"{r['id']} - {r['nome']}" for r in readers]
        self.bookbox['values']=[f"{b['id']} - {b['titulo']} ({b['disponiveis']} disponíveis)" for b in books]
        rmap={r['id']:r['nome'] for r in readers}; bmap={b['id']:b['titulo'] for b in books}
        self.fill(self.loantree,[(x['id'],(x['id'],rmap[x['leitor_id']],bmap[x['livro_id']],x['emprestado_em'],x['previsto_em'],'Ativo' if x['devolvido_em'] is None else 'Devolvido',x['nota'] if x['nota'] is not None else '-')) for x in self.service.dados['emprestimos']])

if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--dados',type=Path,default=Path(__file__).parent/'dados'/'acervo.json'); parser.add_argument('--smoke',action='store_true'); parser.add_argument('--sem-demo',action='store_true')
    args=parser.parse_args(); service=Acervo(args.dados)
    if not args.sem_demo: service.demonstracao()
    root=tk.Tk(); app=App(root,service)
    if args.smoke: root.after(300,root.destroy)
    root.mainloop()

