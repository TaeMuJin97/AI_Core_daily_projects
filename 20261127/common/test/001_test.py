"""TEST 001: 공통 라이브러리 import 및 실제 GPU 연산 검증. 실행: python -m test.001_test."""


def main():
    import sys, torch
    import langchain, langchain_core, langchain_openai, psycopg, sentence_transformers
    print('Python:', sys.executable)
    print('PyTorch:', torch.__version__)
    print('CUDA:', torch.version.cuda)
    print('Available:', torch.cuda.is_available())
    print('GPU Count:', torch.cuda.device_count())
    assert torch.cuda.is_available() and torch.cuda.device_count() >= 1
    print('GPU:', torch.cuda.get_device_name(0))
    x = torch.tensor([1., 2., 3.], device='cuda:0')
    result = x * 2
    torch.cuda.synchronize()
    print('Result:', result)
    assert result.device.type == 'cuda' and result.cpu().tolist() == [2., 4., 6.]
    print("[PASS] TEST 001")


if __name__ == "__main__":
    main()
