from django.urls import path
from .views import funcionario, instituicao
urlpatterns= [
    path('funcionario/',  funcionario.lista_funcionario, name='lista_funcionario'),
    path('funcionario/pdf/', funcionario.funcionario_pdf, name='funcionario_pdf'),
    path('funcionario/cadastrar/', funcionario.cadastrar_funcionario, name='cadastrar_funcionario'),
    path('funcionario/<int:pk>/editar/',  funcionario.editar_funcionario, name='editar_funcionario'),
    path('funcionario/<int:pk>/excluir/', funcionario.excluir_funcionario, name='excluir_funcionario'),

    # Rotas instituicao
    path('instituicao/', instituicao.lista_instituicao, name='lista_instituicao'),
    path('instituicao/pdf/', instituicao.instituicao_pdf, name='instituicao_pdf'),
    path('instituicao/cadastrar/',instituicao.cadastrar_instituicao, name='cadastrar_instituicao'),
    path('instituicao/<int:pk>/editar/', instituicao.editar_instituicao, name='editar_instituicao'),
    path('instituicao/<int:pk>/excluir/', instituicao.excluir_instituicao, name='excluir_instituicao'),

    # Autenticação
 
    path('login/', funcionario.login_funcionario, name='login_funcionario'),
    path('logout/', funcionario.logout_funcionario, name='logout_funcionario'),
    path('', funcionario.area_funcionario, name='area_funcionario'),

]