from decorators import KoandaLogger

test_logger = KoandaLogger(name="poogie_logger")

@test_logger.koanda_logger(log_args=True, log_result=True)
def test_func(a: int, b: int) -> int:
    """
    Print sum of two numbers
    """
    return a+b

if __name__ == "__main__":
    print(test_func(10, 15))