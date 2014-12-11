# -*- coding: utf-8 -*-

def ws():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

@service.xmlrpc
@service.jsonrpc 
def signature():
    data = dict(
        signature=dict(args='none'),
        activation=dict(customer='CNPJ do cliente', key='chave do contrato'),
        )
    return data


@service.xmlrpc
@service.jsonrpc 
def activation(customer, key):
    result = dict(
        code=101,
        message='Error',
        contract_key=key,
        items=[])
    contract = db(db.mul_contract.licence_key == key).select().first()
    if contract:
        if not contract.is_active:
            result['message'] = 'Contract inactive!'
            return result
        if contract.validate < date.today():
            result['message'] = 'Contract expired!'
            return result

        items = db((db.mul_contract_items.contract_id == contract.id) & (db.mul_contract_items.is_active == True)).select()
        for item in items:
            result['items'].append(item.licence_key)

        result['code'] = 100
        result['message'] = 'Success'
    else:
        result['message'] = 'Contract not found!'

    return result
