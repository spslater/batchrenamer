"""BatchRenamer Tests"""
import unittest
from io import StringIO
from os import makedirs
from os.path import isfile, join
from shutil import rmtree
from unittest import mock

from batchrenamer import BatchRenamer


class BatchRenamerTests(unittest.TestCase):
    """Test functionality of BatchRenamer"""

    @staticmethod
    def _make_clean(dirname):
        rmtree(dirname, ignore_errors=True)
        makedirs(dirname, exist_ok=True)

    @staticmethod
    def _touch(filename):
        open(filename, "a").close()

    @classmethod
    def setUpClass(cls):
        cls.res = "test/res"
        cls._make_clean(cls.res)
        cls.original1 = join(cls.res, "file.txt")

    @classmethod
    def tearDownClass(cls):
        rmtree(cls.res, ignore_errors=True)

    def setUp(self):
        # self._make_clean(self.res)
        self._touch(self.original1)
        self.brp = BatchRenamer(self.original1)

    def test_list(self):
        """List files"""
        resp_args = self.brp.parser.parse_args(["list"])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)

        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[0], self.original1)
        self.assertEqual(values[1], self.original1)

    def test_insert(self):
        """Insert value at position x"""
        resp_args = self.brp.parser.parse_args(["insert", "_", "1", "-c"])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[1], self.original1)
        self.assertEqual(values[2], join(self.res, "f_ile.txt"))

    def test_extension(self):
        """Change file extension"""
        resp_args = self.brp.parser.parse_args(["ext", "tsv", "file"])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[0], self.original1)
        self.assertEqual(values[1], join(self.res, "file.tsv"))

    def test_replace(self):
        """Find and replace"""
        resp_args = self.brp.parser.parse_args(["re", "file", "bar"])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[0], self.original1)
        self.assertEqual(values[1], join(self.res, "bar.txt"))

    def test_undo(self):
        """Undo change to filenames"""
        resp_args = self.brp.parser.parse_args(["re", "file", "bar"])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[1], join(self.res, "bar.txt"))

        resp_args = self.brp.parser.parse_args(["undo"])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[1], self.original1)

    def test_save(self):
        """Save changes to filenames"""
        resp_args = self.brp.parser.parse_args(["re", "file", "bar"])
        with mock.patch("sys.stdout", new_callable=StringIO):
            resp_args.func(resp_args)
        resp_args = self.brp.parser.parse_args(["save", "-c"])
        with mock.patch("sys.stdout", new_callable=StringIO):
            resp_args.func(resp_args)
        self.assertTrue(isfile(join(self.res, "bar.txt")))

    def test_quit(self):
        """Quit the program"""
        resp_args = self.brp.parser.parse_args(["quit", "-c"])
        with mock.patch("sys.stdout", new_callable=StringIO):
            self.assertRaises(
                SystemExit,
                resp_args.func,
                resp_args,
            )

    def test_write(self):
        """Save changes to filenames an quit"""
        resp_args = self.brp.parser.parse_args(["re", "file", "bar"])
        with mock.patch("sys.stdout", new_callable=StringIO):
            resp_args.func(resp_args)
            resp_args = self.brp.parser.parse_args(["write", "-c"])
            self.assertRaises(
                SystemExit,
                resp_args.func,
                resp_args,
            )
        self.assertTrue(isfile(join(self.res, "bar.txt")))

    def test_append(self):
        """Append names to files"""
        ep_list = join(self.res, "eps.tsv")
        ep1 = join(self.res, "Show - 0101.txt")
        ep1_title = join(self.res, "Show - 0101 Foo.txt")
        ep2 = join(self.res, "Show - s01e02 -.txt")
        ep2_title = join(self.res, "Show - s01e02 - Bar.txt")
        self._touch(ep1)
        self._touch(ep2)
        with open(ep_list, "w+") as fp:
            fp.write("0101 Foo\ns01e02 Bar")
        self.brp = BatchRenamer(ep1, ep2)
        resp_args = self.brp.parser.parse_args(["ap", "-f", ep_list])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[0], ep1)
        self.assertEqual(values[1], ep1_title)
        self.assertEqual(values[3], ep2)
        self.assertEqual(values[4], ep2_title)

    def test_prepend(self):
        """Prepend numbers to files"""
        tr_list = join(self.res, "trs.tsv")
        tr1 = join(self.res, "Foo.txt")
        tr1_title = join(self.res, "01 Foo.txt")
        tr2 = join(self.res, "Bar.txt")
        tr2_title = join(self.res, "02 Bar.txt")
        self._touch(tr1)
        self._touch(tr2)
        with open(tr_list, "w+") as fp:
            fp.write("Foo 01\nBar 02")
        self.brp = BatchRenamer(tr1, tr2)
        resp_args = self.brp.parser.parse_args(["pre", "-f", tr_list])
        with mock.patch("sys.stdout", new_callable=StringIO) as mock_stdout:
            resp_args.func(resp_args)
        values = mock_stdout.getvalue().splitlines()
        self.assertEqual(values[0], tr1)
        self.assertEqual(values[1], tr1_title)
        self.assertEqual(values[3], tr2)
        self.assertEqual(values[4], tr2_title)
