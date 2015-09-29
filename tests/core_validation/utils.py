from graphql.core.validation import validate
from graphql.core.language.parser import parse
from graphql.core.type import (
    GraphQLSchema,
    GraphQLObjectType,
    GraphQLField,
    GraphQLArgument,
    GraphQLID,
    GraphQLNonNull,
    GraphQLString,
    GraphQLInt,
    GraphQLFloat,
    GraphQLBoolean,
    GraphQLInterfaceType,
    GraphQLEnumType,
    GraphQLEnumValue,
    GraphQLInputObjectType,
    GraphQLUnionType,
    GraphQLList)
from graphql.core.error import format_error

Being = GraphQLInterfaceType('Being', {
    'name': GraphQLField(GraphQLString, {
        'surname': GraphQLArgument(GraphQLBoolean),
    })
})

Pet = GraphQLInterfaceType('Pet', {
    'name': GraphQLField(GraphQLString, {
        'surname': GraphQLArgument(GraphQLBoolean),
    }),
})

DogCommand = GraphQLEnumType('DogCommand', {
    'SIT': GraphQLEnumValue(0),
    'HEEL': GraphQLEnumValue(1),
    'DOWN': GraphQLEnumValue(2),
})

Dog = GraphQLObjectType('Dog', {
    'name': GraphQLField(GraphQLString, {
        'surname': GraphQLArgument(GraphQLBoolean),
    }),
    'nickname': GraphQLField(GraphQLString),
    'barks': GraphQLField(GraphQLBoolean),
    'doesKnowCommand': GraphQLField(GraphQLBoolean, {
        'dogCommand': GraphQLArgument(DogCommand)
    })
}, interfaces=[Being, Pet], is_type_of=lambda: None)

Cat = GraphQLObjectType('Cat', lambda: {
    'furColor': GraphQLField(FurColor)
}, interfaces=[Being, Pet], is_type_of=lambda: None)

CatOrDog = GraphQLUnionType('CatOrDog', [Dog, Cat])

Intelligent = GraphQLInterfaceType('Intelligent', {
    'iq': GraphQLField(GraphQLInt),
})

Human = GraphQLObjectType(
    name='Human',
    interfaces=[Being, Intelligent],
    is_type_of=lambda: None,
    fields={
        'name': GraphQLField(GraphQLString, {
            'surname': GraphQLArgument(GraphQLBoolean),
        }),
        'pets': GraphQLField(GraphQLList(Pet)),
        'iq': GraphQLField(GraphQLInt),
    },
)

Alien = GraphQLObjectType(
    name='Alien',
    is_type_of=lambda *args: True,
    interfaces=[Being, Intelligent],
    fields={
        'iq': GraphQLField(GraphQLInt),
        'name': GraphQLField(GraphQLString, {
            'surname': GraphQLField(GraphQLBoolean),
        }),
        'numEyes': GraphQLField(GraphQLInt),
    },
)

DogOrHuman = GraphQLUnionType('DogOrHuman', [Dog, Human])

HumanOrAlien = GraphQLUnionType('HumanOrAlien', [Human, Alien])

FurColor = GraphQLEnumType('FurColor', {
    'BROWN': GraphQLEnumValue(0),
    'BLACK': GraphQLEnumValue(1),
    'TAN': GraphQLEnumValue(2),
    'SPOTTED': GraphQLEnumValue(3),
})

ComplexInput = GraphQLInputObjectType('ComplexInput', {
    'requiredField': GraphQLField(GraphQLNonNull(GraphQLBoolean)),
    'intField': GraphQLField(GraphQLInt),
    'stringField': GraphQLField(GraphQLString),
    'booleanField': GraphQLField(GraphQLBoolean),
    'stringListField': GraphQLField(GraphQLList(GraphQLString)),
})

ComplicatedArgs = GraphQLObjectType('ComplicatedArgs', {
    'intArgField': GraphQLField(GraphQLString, {
        'intArg': GraphQLArgument(GraphQLInt)
    }),
    'nonNullIntArgField': GraphQLField(GraphQLString, {
        'nonNullIntArg': GraphQLArgument(GraphQLNonNull(GraphQLInt))
    }),
    'stringArgField': GraphQLField(GraphQLString, {
        'stringArg': GraphQLArgument(GraphQLString)
    }),
    'booleanArgField': GraphQLField(GraphQLString, {
        'booleanArg': GraphQLArgument(GraphQLBoolean)
    }),
    'enumArgField': GraphQLField(GraphQLString, {
        'enumArg': GraphQLArgument(FurColor)
    }),
    'floatArgField': GraphQLField(GraphQLString, {
        'floatArg': GraphQLArgument(GraphQLFloat)
    }),
    'idArgField': GraphQLField(GraphQLString, {
        'idArg': GraphQLArgument(GraphQLID)
    }),
    'stringListArgField': GraphQLField(GraphQLString, {
        'stringListArg': GraphQLArgument(GraphQLList(GraphQLString))
    }),
    'complexArgField': GraphQLField(GraphQLString, {
        'complexArg': GraphQLArgument(ComplexInput)
    }),
    'multipleReqs': GraphQLField(GraphQLString, {
        'req1': GraphQLArgument(GraphQLNonNull(GraphQLInt)),
        'req2': GraphQLArgument(GraphQLNonNull(GraphQLInt)),
    }),
    'multipleOpts': GraphQLField(GraphQLString, {
        'opt1': GraphQLArgument(GraphQLInt, 0),
        'opt2': GraphQLArgument(GraphQLInt, 0)
    }),
    'multipleOptsAndReq': GraphQLField(GraphQLString, {
        'req1': GraphQLArgument(GraphQLNonNull(GraphQLInt)),
        'req2': GraphQLArgument(GraphQLNonNull(GraphQLInt)),
        'opt1': GraphQLArgument(GraphQLInt, 0),
        'opt2': GraphQLArgument(GraphQLInt, 0)
    })
})

QueryRoot = GraphQLObjectType('QueryRoot', {
    'human': GraphQLField(Human, {
        'id': GraphQLArgument(GraphQLID),
    }),
    'dog': GraphQLField(Dog),
    'pet': GraphQLField(Pet),
    'catOrDog': GraphQLField(CatOrDog),
    'humanOrAlien': GraphQLField(HumanOrAlien),
    'complicatedArgs': GraphQLField(ComplicatedArgs),
})

default_schema = GraphQLSchema(query=QueryRoot)


def expect_valid(schema, rules, query):
    errors = validate(schema, parse(query), rules)
    assert errors == [], 'Should validate'


def sort_lists(value):
    if isinstance(value, dict):
        new_mapping = []
        for k, v in value.items():
            new_mapping.append((k, sort_lists(v)))
        return sorted(new_mapping)
    elif isinstance(value, list):
        return sorted(map(sort_lists, value))
    return value


def expect_invalid(schema, rules, query, expected_errors, sort_list=True):
    errors = validate(schema, parse(query), rules)
    assert errors, 'Should not validate'
    for error in expected_errors:
        error['locations'] = [
            {'line': loc.line, 'column': loc.column}
            for loc in error['locations']
        ]
    if sort_list:
        assert sort_lists(list(map(format_error, errors))) == sort_lists(expected_errors)

    else:
        assert list(map(format_error, errors)) == expected_errors


def expect_passes_rule(rule, query):
    return expect_valid(default_schema, [rule], query)


def expect_fails_rule(rule, query, errors, sort_list=True):
    return expect_invalid(default_schema, [rule], query, errors, sort_list)


def expect_fails_rule_with_schema(schema, rule, query, errors, sort_list=True):
    return expect_invalid(schema, [rule], query, errors, sort_list)


def expect_passes_rule_with_schema(schema, rule, query):
    return expect_valid(schema, [rule], query)
