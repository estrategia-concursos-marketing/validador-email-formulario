import json
import smtplib
import requests
import dns.resolver
import urllib.parse

"""
 MICROSERVIÇO para levar as leads do formulário aos respectivos lugares. 
  Criado com framework serverless. Usado a conta do MKT/BI para hospedar o microserviço. Para acessar o repositório, confira:
    https://github.com/estrategia-concursos-marketing/microservico-marketing-salescloud

  PROCESSO:
  1. Valida o email, respondendo sucesso ou não. Resposta no front se não for um email válido;
  2. Envia os dados para o Marketing Cloud nas respectivas bases:
    a. Leads_Gerais_5
    b. Total_Base_Geral_
    Lembrando que para acessar essas informações, elas estão salvas como variáveis no Lambda.
  3. Envia os dados para as leads no SalesCloud, para uso do comercial.

  Qualquer PROBLEMA, entre em contato com a equipe de BI e CRM, responsáveis pela produção desse microserviço.
"""

# context = '1'
# event = {"body": "data=%7B%22oid%22%3A%2200D41000001Q9k8%22%2C%22retURL%22%3A%22https%3A%2F%2Fwww.estrategiaconcursos.com.br%2Fgratis%2Fsucesso%2F%22%2C%22Cidade_OrigemIP__c%22%3A%22Barueri%22%2C%22Estado_OrigemIP__c%22%3A%22Sao+Paulo%22%2C%22Modo_de_entrada__c%22%3A%22landing-page%22%2C%22lead_source%22%3A%22Landing+Page%22%2C%22Area_de_Interesse__c%22%3A%22tribunais%22%2C%22Concurso_de_Interesse__c%22%3A%22%22%2C%22Interesse_Evento__c%22%3A%22%22%2C%22recordType%22%3A%2201241000001AP21%22%2C%22first_name%22%3A%22israel%22%2C%22email%22%3A%22israel.mendes%40estrategiaconcursos.com.br%22%2C%22phone%22%3A%22(55)+11944-6919%22%7D", "isBase64Encoded": 0}

def verify(event, context):
    event1 = json.loads(urllib.parse.parse_qs(event['body'])['data'][0])
    
    def emailValidator(email):
        splitAddress = email.split('@')
        domain = str(splitAddress[1])

        # try:
        #     records = dns.resolver.query(domain, 'MX')
        # except:
        #     return 'notExistingEmail'
        
        records = dns.resolver.query(domain, 'MX')
        mxRecord = records[0].exchange
        mxRecord = str(mxRecord)

        server = smtplib.SMTP()
        server.set_debuglevel(0)
        server.connect(mxRecord)
        server.helo(server.local_hostname)
        server.mail(email)
        
        code, message = server.rcpt(str(email))
        server.quit()

        if code == 250:
            return 'existingEmail'
        else:
            return 'notExistingEmail'
    
    email = event1['email']

    # Principal do Microserviço
    if emailValidator(email) == 'notExistingEmail':
        body = {
            'message': 'Email nao existente. Retornar para o usuario.',
            'input': email
        }
        response = {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(body)
        }
        print(response)
        return response
    else:
        body = {
            'message': 'Email existente. Continue.',
            'input': email
        }
        response = {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Credentials": True,
                "Access-Control-Allow-Origin": "*",
                "Content-Type": "application/json"
            },
            'body': json.dumps(body)
        }
        print(response)
        return response

# verify(event, context)
