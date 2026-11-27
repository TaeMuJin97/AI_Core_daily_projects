"""TEST 000: 설치 전 CUDA PyTorch 및 인터프리터 확인. 실행: python -m test.000_test."""


def main():
    import sys
    print('Python:', sys.executable)
    try:
        import torch
    except ImportError:
        raise SystemExit('torch 미설치: 호환 CUDA PyTorch를 먼저 설치하세요.') from None
    print('PyTorch:', torch.__version__)
    print('CUDA:', torch.version.cuda)
    print('Available:', torch.cuda.is_available())
    print('GPU Count:', torch.cuda.device_count())
    assert torch.cuda.is_available() and torch.cuda.device_count() >= 1, 'CUDA 사용 불가: 설치/드라이버 확인'
    print('GPU:', torch.cuda.get_device_name(0))
    print("[PASS] TEST 000")


if __name__ == "__main__":
    main()
