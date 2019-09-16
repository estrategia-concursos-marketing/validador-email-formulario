import json
import smtplib
import requests
import dns.resolver
import urllib.parse

"""

 MICROSERVIÇO para validar as leads do email para o formulário. 
 Lembrando que o REGEX é validado no front, mas aqui é feito pelo MX e SMTP.
 Qualquer PROBLEMA, entre em contato com a equipe de BI e CRM, responsáveis pela produção desse microserviço.

"""

# context = '1'
# event = {"body": "data=%7B%22oid%22%3A%2200D41000001Q9k8%22%2C%22retURL%22%3A%22https%3A%2F%2Fwww.estrategiaconcursos.com.br%2Fgratis%2Fsucesso%2F%22%2C%22Cidade_OrigemIP__c%22%3A%22Barueri%22%2C%22Estado_OrigemIP__c%22%3A%22Sao+Paulo%22%2C%22Modo_de_entrada__c%22%3A%22landing-page%22%2C%22lead_source%22%3A%22Landing+Page%22%2C%22Area_de_Interesse__c%22%3A%22tribunais%22%2C%22Concurso_de_Interesse__c%22%3A%22%22%2C%22Interesse_Evento__c%22%3A%22%22%2C%22recordType%22%3A%2201241000001AP21%22%2C%22first_name%22%3A%22israel%22%2C%22email%22%3A%22israel.mendes%40estrategiaconcursos.com.br%22%2C%22phone%22%3A%22(55)+11944-6919%22%7D", "isBase64Encoded": 0}

def verify(event, context):
    print("Event Antes da Transformação: ", event)
    print("Context Antes da Transformação: ", context)
    event1 = json.loads(urllib.parse.parse_qs(event['body'])['data'][0])
    print("Event Pós-Transformação: ", event1)
    
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
    print("Email: ", email)

    # Principal do Microserviço
    if emailValidator(email) == 'notExistingEmail':
        body = {
            'message': 'Email nao existente. Retornar para o usuario.',
            'input': email
        }
        response = {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
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
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": True,
                "Content-Type": "application/json"
            },
            'body': json.dumps(body)
        }
        print(response)
        return response

# verify(event, context)
