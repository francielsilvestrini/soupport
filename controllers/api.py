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


contract_results = {
    100: 'Success',
    101: 'Error',
    102: 'Customer Registry not found!',
    103: 'Bad record for the contract!',
    104: 'Contract inactive!',
    105: 'Contract expired!',
}


@service.xmlrpc
@service.jsonrpc
def contract(registry, contract_number):
    result = Dict(
        code=101,
        message=contract_results[101]
        )
    contract = Dict(
        registry='',
        name='',
        number='',
        licence_key='',
        items=[],
        )

    customer = db(db.customer.registry==registry).select().first()
    if customer:
        rcontract = db(db.mul_contract.number == contract_number).select().first()
        if rcontract.customer_id == customer.id:
            if rcontract.is_active:
                if rcontract.validate >= date.today():
                    result.code = 100
                    contract.registry = customer.registry
                    contract.name = customer.name
                    contract.number = rcontract.number
                    contract.licence_key = rcontract.licence_key

                    items = db((db.mul_contract_items.contract_id == rcontract.id) \
                        & (db.mul_contract_items.is_active == True)).select()
                    for item in items:
                        product = Dict(
                            number=item.mul_product.number,
                            name=item.mul_product.name,
                            licence_key=item.mul_contract_items.licence_key,
                            )
                        contract.items.append(product)
                else:
                    result.code = 105
            else:
                result.code = 104
        else:
            result.code = 103
    else:
        result.code = 102
    result.message = contract_results[result.code]

    return dict(result=result, contract=contract)