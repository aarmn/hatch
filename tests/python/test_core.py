import pytest

from hatch.python.core import get_distribution
from hatch.python.distributions import DISTRIBUTIONS
from hatch.utils.network import download_file
from hatch.utils.structures import EnvVars


def test_unknown_distribution():
    with pytest.raises(ValueError, match='Unknown distribution: foo'):
        get_distribution('foo')


@pytest.mark.parametrize('name', DISTRIBUTIONS)
def test_executable(temp_dir, platform, name):
    dist = get_distribution(name)
    archive_path = temp_dir / dist.archive_name
    dist_path = temp_dir / 'dist'

    download_file(archive_path, dist.source, follow_redirects=True)
    dist.unpack(archive_path, dist_path)

    python_path = dist_path / dist.python_path
    assert python_path.is_file()

    output = platform.check_command_output([python_path, '-c', 'import sys;print(sys.executable)']).strip()
    assert output == str(python_path)

    major_minor = name.replace('pypy', '')

    output = platform.check_command_output([python_path, '--version']).strip()
    assert output.startswith(f'Python {major_minor}.')
    if name.startswith('pypy'):
        assert 'PyPy' in output


@pytest.mark.parametrize(
    'system, variant',
    [
        ('windows', 'shared'),
        ('windows', 'static'),
        ('linux', 'v1'),
        ('linux', 'v2'),
        ('linux', 'v3'),
        ('linux', 'v4'),
    ],
)
def test_variants(platform, system, variant):
    if platform.name != system:
        pytest.skip(f'Skipping test for: {system}')

    with EnvVars({f'HATCH_PYTHON_VARIANT_{system.upper()}': variant}):
        dist = get_distribution('3.11')

    assert variant in dist.source
