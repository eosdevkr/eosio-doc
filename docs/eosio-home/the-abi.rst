2.3 ABI 파일 이해하기
========================

.. rubric:: 도입

이전 장에서는 제공된 ABI 파일을 사용하여 ``eosio.token`` 컨트랙트를 배포하였다.
이번 튜토리얼에서 ABI 파일과 ``eosio.token`` 컨트랙트가 어떠한 연관관계를 갖고 있는지 간략히 살펴볼 것이다. 

ABI 파일은 ``eosio.cdt`` 에서 제공하는 ``eosio-cpp`` 유틸리티를 이용하여 생성할 수 있다. 
하지만 ABI의 생성에 오작동이 생기거나 실패하게 하는 몇 가지 상황이 있다.
고급 C++ 패턴에서 실수를 하거나, 때때로 커스텀 타입이 ABI 생성에 문제를 일으키기도 한다.
이러한 이유에서 어떻게 ABI 파일이 작동하는지 **반드시** 이해해야 하며, 필요한 경우 디버깅하거나 수정할 수 있어야 한다.

.. rubric:: ABI는 무엇인가?

Application Binary Interface(ABI)는 사용자 액션의 JSON과 Binary 표현 간에 어떻게 변환해야 하는지 JSON 형식으로 기술한 것이다.
또한 ABI는 데이터베이스 상태(database state)를 JSON으로/에서 어떻게 변환할 것인지도 기술한다.
일단 ABI를 사용하여 컨트랙트를 기술하고 나면, 개발자와 사용자는 JSON을 통해 컨트랙트와 매끄럽게 상호작용할 수 있게 된다.

.. warning:: Security Note

트랜잭션은 ABI를 우회해서도 실행할 수 있다.
컨트랙트에 전달한 메시지와 액션이 반드시 ABI와 일치할 필요는 없다.
ABI는 일종의 가이드지, 문지기가 아니다.

.. rubric:: ABI 파일 생성하기

비어있는 ABI를 만들고 이름은 ``eosio.token.abi`` 라고 하자.

.. code-block:: JSON

  {
    "version": "eosio::abi/1.0",
    "types": [],
    "structs": [],
    "actions": [],
    "tables": [],
    "ricardian_clauses": [],
    "abi_extensions": [],
    "___comment" : ""
  }

.. rubric:: 타입

클라이언트나 인터페이스는 ABI를 사용하여 컨트랙트를 해석하거나 GUI를 생성할 수 있다.
일관된 방식으로 처리하기 위하여, 퍼블릭 액션에서 매개 변수로 사용하는 커스텀 타입이나 ABI에서 기술하는 구조체에 대해 작성해야 한다.

.. rubric:: 기본제공 타입

EOSIO은 다양한 커스텀 내장 타입을 구현해놓고 있다. 
내장된 기본 타입들은 ABI 파일 내에서 기술할 필요가 없다. 
EOSIO 내장 타입들에 익숙해지고 싶다면 `이곳 <https://github.com/EOSIO/eos/blob/master/libraries/chain/abi_serializer.cpp#L65-L103/>`_ 의 정의를 참고하라.

.. code-block:: JSON
  
  {
    "new_type_name": "name",
    "type": "name"
  }

ABI는 아래와 같이 표현된다.

.. code-block:: JSON
  
  {
    "version": "eosio::abi/1.0",
    "types": [{
      "new_type_name": "name",
      "type": "name"
	  }],
    "structs": [],
    "actions": [],
    "tables": [],
    "ricardian_clauses": [],
    "abi_extensions": []
  }

.. rubric:: 구조체

ABI에 노출해야 하는 구조체도 기술해야 한다.
eosio.token.hpp을 보면, 퍼블릭 액션에서 어떤 구조체를 사용하고 있는지 확인할 수 있다.
이것은 다음 단계에서 특히 중요하다. 

구조체 객체의 JSON 정의는 다음과 같다.

.. code-block:: JSON

  {
    "name": "issue", //The name 
    "base": "",      //Inheritance, parent struct
    "fields": []     //Array of field objects describing the struct's fields. 
  }

.. rubric:: 필드

.. code-block:: JSON

  {
    "name":"", // The field's name
    "type":""  // The field's type
  }

``eosio.token`` 컨트랙트에는 정의해야 하는 다수의 구조체가 있다.
주의해야 할 것은 몇몇 action의 매개변수에 대한 명시적 정의가 필요한 것일뿐 모든 구조체의 명시적 정의가 필요한 것은 아니라는 것이다.     
``eosio.token`` 컨트랙트의 ABI에서 기술해야 하는 구조체는 다음과 같다.

.. rubric:: 묵시적 구조체

묵시적 구조체는 컨트랙트에서 명시적으로 정의하고 있지 않은 것이다.
`create action <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L24>`_ 을 보면, 두가지 매개변수가 있는데 ``name`` 타입의 ``issuer`` 와 ``asset`` 타입의 ``maximum_supply`` 다.
튜토리얼에서 모든 구조체를 분석하지는 않겠지만, 같은 논리를 적용하면 다음과 같은 결과를 얻을 수 있다.

`create <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L25>`_

.. code-block:: JSON

  {
    "name": "create",
    "base": "",
    "fields": [
      {
        "name":"issuer", 
        "type":"name"
      },
      {
        "name":"maximum_supply", 
        "type":"asset"
      }
    ]
  }

`issue <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L29>`_

.. code-block:: JSON

  {
    "name": "issue",
    "base": "",
    "fields": [
      {
        "name":"to", 
        "type":"name"
      },
      {
        "name":"quantity", 
        "type":"asset"
      },
      {
        "name":"memo", 
        "type":"string"
      }
    ]
  }

`retire <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L32>`_

.. code-block:: JSON

  {
    "name": "retire",
    "base": "",
    "fields": [
      {
        "name":"quantity", 
        "type":"asset"
      },
      {
        "name":"memo", 
        "type":"string"
      }
    ]
  }

`transfer <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L35-L38>`_

.. code-block:: JSON

  {
    "name": "transfer",
    "base": "",
    "fields": [
      {
        "name":"from", 
        "type":"name"
      },
      {
        "name":"to", 
        "type":"name"
      },
      {
        "name":"quantity", 
        "type":"asset"
      },
      {
        "name":"memo", 
        "type":"string"
      }
    ]
  }

`close <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L44>`_

.. code-block:: JSON

  {
    "name": "close",
    "base": "",
    "fields": [
      {
        "name":"owner", 
        "type":"name"
      },
      {
        "name":"symbol", 
        "type":"symbol"
      }
    ]
  }

.. rubric:: 명시적 구조체

멀티 인덱스 테이블에서 명시적 구조체를 인스턴스화 하기 위하여 이를 명시적으로 정의해야 한다.
앞서 묵시적 구조체를 정의한 것과 동일한 방식으로 명시적 구조체도 정의한다.

`account <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L61-L65>`_

.. code-block:: JSON

  {
    "name": "account",
    "base": "",
    "fields": [
      {
        "name":"balance", 
        "type":"asset"
      }
    ]
  }

`currency_stats <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L67-L73>`_

.. code-block:: JSON

  {
    "name": "currency_stats",
    "base": "",
    "fields": [
      {
        "name":"supply", 
        "type":"asset"
      },
      {
        "name":"max_supply", 
        "type":"asset"
      },
      {
        "name":"issuer", 
        "type":"account_name"
      }
    ]
  }

.. rubric:: 액션

액션의 JSON 객체 정의는 다음과 같다.

.. code-block:: JSON

  {
    "name": "transfer",       //The name of the action as defined in the contract
    "type": "transfer",       //The name of the implicit struct as described in the ABI
    "ricardian_contract": ""  //An optional ricardian clause to associate to this action describing its intended functionality.
  }

``eosio.token`` 컨트랙트의 `헤더 파일<https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L24-L36>`_ 에서 기술한 모든 퍼블릭 함수들을 종합하여 ``eosio.token`` 컨트랙트의 액션을 기술한다.
각 액션의 *타입* 은 앞에서 기술한 구조체가 된다.
대부분의 경우 함수명과 구조체 이름은 같겠지만, 반드시 같아야만 하는 것은 아니다.

아래는 각 액션이 어떻게 기술되어 있는지 나타낸 JSON 예시와 소스 코드가 연결된 액션의 목록이다.

`create <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L24-L25>`_

.. code-block:: JSON
  
  {
    "name": "create",
    "type": "create",
    "ricardian_contract": ""
  }

`issue <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L27>`_

.. code-block:: JSON
  
  {
    "name": "issue",
    "type": "issue",
    "ricardian_contract": ""
  } 

`retire <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L31-L34>`_

.. code-block:: JSON
  
  {
    "name": "retire",
    "type": "retire",
    "ricardian_contract": ""
  }

`transfer <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L34-L38>`_

.. code-block:: JSON
  
  {
    "name": "transfer",
    "type": "transfer",
    "ricardian_contract": ""
  }

`close <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L44>`_

.. code-block:: JSON
  
  {
    "name": "close",
    "type": "close",
    "ricardian_contract": ""
  }

.. rubric:: 테이블

다음은 테이블 JSON 객체 정의이다.

.. code-block:: JSON
  
  {
    "name": "",       //The name of the table, determined during instantiation. 
    "type": "",       //The table's corresponding struct
    "index_type": "", //The type of primary index of this table
    "key_names" : [], //An array of key names, length must equal length of key_types member
    "key_types" : []  //An array of key types that correspond to key names array member, length of array must equal length of key names array.
  }

eosio.token 컨트랙트는 두 개의 테이블, `accounts <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L75>`_ 와 `stat <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L76>`_ 을 인스턴스화 한다.

`account 구조체 <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L61-L65>`_ 에 기반한 accounts 테이블은 i64 인덱스로 `uint64 를 기본키 <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L64>`_ 로 사용한다.

다음은 accounts 테이블이 ABI에서 어떻게 기술되어있는지 보여준다.

.. code-block:: JSON

  {
    "name": "accounts",
    "type": "account", // Corresponds to previously defined struct
    "index_type": "i64",
    "key_names" : ["primary_key"],
    "key_types" : ["uint64"]
  }
  
`currency_stats 구조체 <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L67-L73>`_ 에 기반한 stat 테이블은 i64 인덱스로 `uint64 를 기본키 <https://github.com/EOSIO/eosio.contracts/blob/master/eosio.token/include/eosio.token/eosio.token.hpp#L72>`_ 로 사용한다.

다음은 stat 테이블이 ABI에서 어떻게 기술되어있는지 보여준다.

.. code-block:: JSON

  {
    "name": "stat",
    "type": "currency_stats",
    "index_type": "i64",
    "key_names" : ["primary_key"],
    "key_types" : ["uint64"]
  }

이를 통해 테이블들이 동일한 "key name"을 갖고 있다는 것을 눈치챘을 것이다. 
키들를 유사한 이름으로 지정함으로써 테이블간 관계를 암시적으로 나타낼 수 있다는 점에서 의미가 있다.
이러한 구현 방식은, 주어진 값을 테이블의 쿼리에 이용할 수 있다는 것을 의미한다.

.. rubric:: 종합

최종적으로 ``eosio.token`` 컨트랙트를 정확하게 기술한 ABI 파일은 다음과 같다.

.. code-block:: JSON
  
  {
    "version": "eosio::abi/1.0",
    "types": [
      {
        "new_type_name": "name",
        "type": "name"
      }
    ],
    "structs": [
      {
        "name": "create",
        "base": "",
        "fields": [
          {
            "name":"issuer", 
            "type":"name"
          },
          {
            "name":"maximum_supply", 
            "type":"asset"
          }
        ]
      },
      {
        "name": "issue",
        "base": "",
        "fields": [
            {
              "name":"to", 
              "type":"name"
            },
            {
              "name":"quantity", 
              "type":"asset"
            },
            {
              "name":"memo", 
              "type":"string"
            }
        ]
      },
      {
        "name": "retire",
        "base": "",
        "fields": [
            {
              "name":"quantity", 
              "type":"asset"
            },
            {
              "name":"memo", 
              "type":"string"
            }
        ]
      },
      {
        "name": "close",
        "base": "",
        "fields": [
            {
              "name":"owner", 
              "type":"name"
            },
            {
              "name":"symbol", 
              "type":"symbol"
            }
        ]
      },
      {
        "name": "transfer",
        "base": "",
        "fields": [
          {
            "name":"from", 
            "type":"name"
          },
          {
            "name":"to", 
            "type":"name"
          },
          {
            "name":"quantity", 
            "type":"asset"
          },
          {
            "name":"memo", 
            "type":"string"
          }
        ]
      },
      {
        "name": "account",
        "base": "",
        "fields": [
          {
            "name":"balance", 
            "type":"asset"
          }
        ]
      },
      {
        "name": "currency_stats",
        "base": "",
        "fields": [
          {
            "name":"supply", 
            "type":"asset"
          },
          {
            "name":"max_supply", 
            "type":"asset"
          },
          {
            "name":"issuer", 
            "type":"name"
          }
        ]
      }
    ],
    "actions": [
      {
        "name": "transfer",
        "type": "transfer",
        "ricardian_contract": ""
      },
      {
        "name": "issue",
        "type": "issue",
        "ricardian_contract": ""
      },
      {
        "name": "retire",
        "type": "retire",
        "ricardian_contract": ""
      },
      {
        "name": "create",
        "type": "create",
        "ricardian_contract": ""
      },
      {
        "name": "close",
        "type": "close",
        "ricardian_contract": ""
      }
    ],
    "tables": [
      {
        "name": "accounts",
        "type": "account",
        "index_type": "i64",
        "key_names" : ["primary_key"],
        "key_types" : ["uint64"]
      },
      {
        "name": "stat",
        "type": "currency_stats",
        "index_type": "i64",
        "key_names" : ["primary_key"],
        "key_types" : ["uint64"]
      }
    ],
    "ricardian_clauses": [],
    "abi_extensions": []
  }

.. rubric:: 토큰 컨트랙트에서 다루지 않은 케이스

.. rubric:: Vector

ABI에서 vector를 기술하려면 간단히 타입에 ``[]`` 을 추가한다.
permission level의 vector는 ``permission_level[]`` 로 기술한다.

.. rubric:: Struct Base

Struct Base는 많이 사용되지는 않지만 상당히 중요한 속성이다.
구조체 ABI는 동일 ABI 파일 내에 기술된 **base** ABI 구조체를 상속하여 사용할 수 있다.
스마트 컨트랙트 로직이 상속을 지원하지 않을 경우, 에러를 throw할뿐 특별한 이슈를 발생시키지 않는다.

시스템 컨트랙트의 `소스 코드 <https://github.com/EOSIO/eosio.contracts/blob/4e4a3ca86d5d3482dfac85182e69f33c49e62fa9/eosio.system/include/eosio.system/eosio.system.hpp#L46>`_ 와 `ABI <https://github.com/EOSIO/eosio.contracts/blob/4e4a3ca86d5d3482dfac85182e69f33c49e62fa9/eosio.system/abi/eosio.system.abi#L262>`_ 예시를 확인할 수 있다.

.. rubric:: 다루지 않은 그외 ABI 속성

이야기를 줄이기 위해 ABI 속성 중 앞서 다뤄지지 않았던 다른 ABI 속성들에 대해 전체적으로 간략히 이야기 해보겠다.

.. rubric:: 리카디안 절

리카디안 절은 특정 액션에 대한 의도된 결과를 기술한다.
송신자와 컨트랙트간 조건을 설정하는데 이를 사용할 수 있다.

.. rubric:: ABI 확장

일반적인 "future proofing" 계층은 이전 버전의 클라이언트가 확장 데이터의 "청크(chunk)"를 파싱하지 않는 것을 허용한다.
이 속성은 현재 사용하지 않고 있다.
앞으로 확장마다 vector 안에 각각의 "청크"를 갖게 되어 구 버전의 클라이언트는 이를 생략하고 해석하는 법을 아는 새 버전의 클라이언트를 이를 이해할 수 있을 것이다.

.. rubric:: 유지보수

구조체의 변경, 테이블의 추가, 액션 추가, 액션에 매개변수 추가, 새 타입의 사용이 발생하면 ABI도 업데이트해야한다.
ABI 파일을 업데이트 해준다면 대다수의 에러는 발생하지 않을 것이다.

.. rubric:: 문제 해결

.. rubric:: 테이블이 어떤 데이터도 반환하지 않는 경우

테이블이 ABI 파일에 정확하게 기술되어 있는지 확인하라.
예를 들어 ``cleos`` 에서 컨트랙트에 테이블을 잘못된 정의로 추가한 뒤, 테이블에서 데이터를 가져오려고 한다면 비어있는 결과를 수신하게 된다.
``cleos`` 는 데이터를 추가하거나 읽어들일 때 컨트랙트가 ABI 파일에 적절하게 기술되어 있지 않아 동작에 실패하더라도 에러를 발생시키지 않는다.
