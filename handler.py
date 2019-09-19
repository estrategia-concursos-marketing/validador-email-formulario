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

# Para debugar localmente
# context = '1'
# with open('resposta.json') as f:
#     event = json.load(f)
#     print(event)

def verify(event, context):
    print(event)
    # print(email)
    
    def emailValidator(email):
        splitAddress = email.split('@')
        domain = str(splitAddress[1])

        # Aqui validamos se o domínio existe.
        try:
            records = dns.resolver.query(domain, 'MX')
        except:
            return 'notExistingEmail'
        
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

    # Principal do Microserviço
    if event['queryStringParameters'] == None:
        body = {
            'message': 'Email nao foi apresentado no request',
            'input': event
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
        email = event['queryStringParameters']['address']

        try:   
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
        except:
            body = {
                'message': 'Erro no sistema, confira o que aconteceu no log.',
                'input': event
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
            
# verify(event, context)
