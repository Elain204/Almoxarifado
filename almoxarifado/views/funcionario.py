from django.http import HttpResponse
from xhtml2pdf import pisa
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from ..models import Instituicao, Funcionario
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db import transaction
from django.contrib.auth.decorators import login_required

# Login

def login_funcionario(request):
    if request.method == 'POST':
        matricula = request.POST.get('username')
        senha = request.POST.get('password')
        user = authenticate(request, username=matricula, password=senha)
        if user is not None:
            if user.is_superuser: 
                login(request, user)
                return redirect('area_funcionario')
            else: 
                return render(request, 'login.html', {'erro': 'Acesso negado. Apenas usuários administradores podem fazer login.'})
        else:
            return render(request, 'login.html', {'erro': 'Usuário ou senha inválidos'})
            
    return render(request, 'login.html')

@login_required
def logout_funcionario(request):
    logout(request)
    return redirect('login_funcionario')


@login_required
def area_funcionario(request):
    return render(request, 'funcionario/area_funcionario.html')

from django.db.models import Q

@login_required
def lista_funcionario(request):
    query = request.GET.get('q')
    funcionarios = Funcionario.objects.select_related('instituicao').all()

    if query:
        funcionarios = funcionarios.filter(
            Q(nome__icontains=query) 
        )

    return render(request, 'funcionario/lista.html', {'funcionarios': funcionarios})
    



@login_required
def cadastrar_funcionario(request):
    instituicoes = Instituicao.objects.all()
    erros = {}
    val = {}

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        data_nascimento_str = request.POST.get('data_nascimento', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        instituicao_id = request.POST.get('instituicao', '').strip()
        senha = request.POST.get('senha', '').strip()
        username = request.POST.get('username', '').strip()

        val = {
            'nome': nome,
            'data_nascimento': data_nascimento_str,
            'email': email,
            'telefone': telefone,
            'instituicao_id': instituicao_id,
            'username': username,
        }

        if not nome:
            erros['nome'] = 'Nome é obrigatório.'
        if not data_nascimento_str:
            erros['data_nascimento'] = 'Data de nascimento é obrigatória.'
        if not email:
            erros['email'] = 'Email é obrigatório.'
        if not telefone:
            erros['telefone'] = 'Telefone é obrigatório.'
        if not instituicao_id:
            erros['instituicao'] = 'Instituição obrigatória.'
        if not senha:
            erros['senha'] = 'Senha obrigatória.'
        if not username:
            erros['username'] = 'Nome de usuário obrigatório.'

        try:
            data_nascimento = datetime.strptime(
                data_nascimento_str, '%Y-%m-%d').date()
        except ValueError:
            erros['data_nascimento'] = 'Data inválida (formato: AAAA-MM-DD).'

        if User.objects.filter(username=username).exists():
            erros['username'] = 'Já existe um usuário com esse nome.'
        if Funcionario.objects.filter(email=email).exists():
            erros['email'] = 'Já existe um funcionário com esse e-mail.'

        try:
            instituicao = Instituicao.objects.get(pk=instituicao_id)
        except Instituicao.DoesNotExist:
            erros['instituicao'] = 'Instituição inválida.'

        if not erros:
            with transaction.atomic():
                user = User.objects.create_user(
                    username=username, email=email, password=senha)
                Funcionario.objects.create(
                    user=user,
                    nome=nome,
                    data_nascimento=data_nascimento,
                    email=email,
                    telefone=telefone,
                    instituicao=instituicao
                )
                return redirect('lista_funcionario')

    return render(request, 'funcionario/cadastro.html', {
        'instituicoes': instituicoes,
        'erros': erros,
        'val': val
    })


@login_required
def editar_funcionario(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    instituicoes = Instituicao.objects.all()
    erros = {}
    val = {}

    if request.method == 'POST':
        nome = request.POST.get('nome', '').strip()
        data_nascimento_str = request.POST.get('data_nascimento', '').strip()
        email = request.POST.get('email', '').strip()
        telefone = request.POST.get('telefone', '').strip()
        instituicao_id = request.POST.get('instituicao', '').strip()
        senha = request.POST.get('senha', '').strip()

        val = {
            'nome': nome,
            'data_nascimento': data_nascimento_str,
            'email': email,
            'telefone': telefone,
            'instituicao_id': instituicao_id,
        }

        try:
            data_nascimento = datetime.strptime(
                data_nascimento_str, '%Y-%m-%d').date()
        except ValueError:
            erros['data_nascimento'] = 'Data inválida.'

        if Funcionario.objects.exclude(pk=funcionario.pk).filter(email=email).exists():
            erros['email'] = 'Já existe um funcionário com esse e-mail.'

        try:
            instituicao = Instituicao.objects.get(pk=instituicao_id)
        except Instituicao.DoesNotExist:
            erros['instituicao'] = 'Instituição inválida.'

        if not erros:
            with transaction.atomic():
                user = funcionario.user
                user.email = email
                if senha:
                    user.set_password(senha)
                user.save()

                funcionario.nome = nome
                funcionario.data_nascimento = data_nascimento
                funcionario.email = email
                funcionario.telefone = telefone
                funcionario.instituicao = instituicao
                funcionario.save()

                return redirect('lista_funcionario')

    return render(request, 'funcionario/editar.html', {
        'funcionario': funcionario,
        'instituicoes': instituicoes,
        'erros': erros,
        'val': val
    })
@login_required
def excluir_funcionario(request, pk):
    funcionario = get_object_or_404(Funcionario, pk=pk)
    if request.method == 'POST':
        user = funcionario.user
        funcionario.delete()
        user.delete()
    return redirect('lista_funcionario')

 

 
 
@login_required
def funcionario_pdf(request):
    funcionarios_list = Funcionario.objects.all()
    template_path = 'funcionario/pdf.html'
    context = {'funcionarios': funcionarios_list}
    html = render(request, template_path, context).content.decode('utf-8')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="funcionarios.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)

    return response


 