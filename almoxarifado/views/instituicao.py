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

@login_required
def lista_instituicao(request):
    query = request.GET.get('q', '')
    instituicao = Instituicao.objects.all()

    if query:
        instituicao = instituicao.filter(
            Q(nome__icontains=query) | Q(cnpj__icontains=query)
        )

    return render(request, 'instituicao/lista.html', {
        'instituicao': instituicao
    })


@login_required
def cadastrar_instituicao(request):
    if request.method == 'POST':
        nome = request.POST['nome']
        cep = request.POST['cep']
        logradouro = request.POST['logradouro']
        numero = request.POST['numero']
        bairro = request.POST['bairro']
        cidade = request.POST['cidade']
        estado = request.POST['estado']
        telefone = request.POST['telefone']
        cnpj = request.POST['cnpj']

        Instituicao.objects.create(
            nome=nome,
            cep=cep,
            logradouro=logradouro,
            numero=numero,
            bairro=bairro,
            cidade=cidade,
            estado=estado,
            telefone=telefone,
            cnpj=cnpj
        )
        return redirect('lista_instituicao')
    return render(request, 'instituicao/cadastro.html')


@login_required
def editar_instituicao(request, pk):
    instituicao = get_object_or_404(Instituicao, pk=pk)
    if request.method == 'POST':
        instituicao.nome = request.POST['nome']
        instituicao.cep = request.POST['cep']
        instituicao.logradouro = request.POST['logradouro']
        instituicao.numero = request.POST['numero']
        instituicao.bairro = request.POST['bairro']
        instituicao.cidade = request.POST['cidade']
        instituicao.estado = request.POST['estado']
        instituicao.telefone = request.POST['telefone']
        instituicao.cnpj = request.POST['cnpj']
        instituicao.save()
        return redirect('lista_instituicao')
    return render(request, 'instituicao/editar.html', {'instituicao': instituicao})


@login_required
def excluir_instituicao(request, pk):
    instituicao = get_object_or_404(Instituicao, pk=pk)
    if request.method == 'POST':
        instituicao.delete()
    return redirect('lista_instituicao')
@login_required
def instituicao_pdf(request):
    instituicao = Instituicao.objects.all()
    template_path = 'instituicao/pdf.html'
    context = {'instituicao': instituicao}
    html = render(request, template_path, context).content.decode('utf-8')
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="instituicoes.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('Erro ao gerar PDF', status=500)
    return response
