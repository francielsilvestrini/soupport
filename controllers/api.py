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
    106: 'Product licence expired!',
}


@service.xmlrpc
@service.jsonrpc
def contract(registry, contract_number):
    contract = Dict(
        result = dict(
            code=101,
            message=contract_results[101]
            ),
        registry='',
        name='',
        number='',
        licence_key='',
        validate='',
        items=dict(),
        )
    if contract_number in['fleet_demo', 'A']:
        contract.registry = '00.000.000/0000-00'
        contract.name = 'Onnix Sistemas'
        contract.number = contract_number
        contract.licence_key = ''
        contract.validate = str(request.now.today())
        for row in db(db.mul_product).select():
            product = dict(
                code=row.code,
                name=row.name,
                identifier=row.identifier,
                licence_key='',
                validate=str(request.now.today()),
                result = dict(
                    code=100,
                    message=contract_results[100]
                    ),
                )
            products[row.identifier] = product
    else:
        customer = db(db.person.registry==registry).select().first()
        if customer:
            rcontract = db(db.mul_contract.number == contract_number).select().first()
            if rcontract.customer_id == customer.id:
                if rcontract.is_active:
                    if rcontract.validate >= date.today():
                        contract.result['code'] = 100
                    else:
                        contract.result['code'] = 105
                else:
                    contract.result['code'] = 104

                contract.registry = customer.registry
                contract.name = customer.name
                contract.number = rcontract.number
                contract.licence_key = rcontract.licence_key
                contract.validate = str(rcontract.validate)

                items = db((db.mul_contract_items.contract_id == rcontract.id) \
                    & (db.mul_product.id == db.mul_contract_items.product_id) \
                    & (db.mul_contract_items.is_active == True)).select()
                products = dict()
                for item in items:
                    if item.mul_contract_items.validate < date.today():
                        result_code = 106
                    else:
                        result_code = 100

                    product = dict(
                        code=item.mul_product.code,
                        name=item.mul_product.name,
                        identifier=item.mul_product.identifier,
                        licence_key=item.mul_contract_items.licence_key,
                        validate=str(item.mul_contract_items.validate),
                        result = dict(
                            code=result_code,
                            message=contract_results[result_code]
                            ),
                        )
                    products[item.mul_product.identifier] = product
                contract.items = products
            else:
                contract.result['code'] = 103
        else:
            contract.result['code'] = 102
        contract.result['message'] = contract_results[contract.result['code']]
        if contract.result['code'] > 100:
            contract.result['message'] += ' {Registry: %s, Contract Number: %s}' % (registry, contract_number)

    return contract.copy()