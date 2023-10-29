from CONSTANT_POINTS import CONSTANT_POINTS
import functools
from ecdsa.rfc6979 import generate_k
import hashlib
import sympy
import math
from sympy.core.numbers import igcdex
import mpmath
from typing import Tuple 


FIELD_PRIME = 3618502788666131213697322783095070105623107215331596699973092056135872020481
FIELD_GEN = 3
ALPHA = 1
BETA = 3141592653589793238462643383279502884197169399375105820974944592307816406665
EC_ORDER = 3618502788666131213697322783095070105526743751716087489154079457884512865583
HASH_BYTES = 32



N_ELEMENT_BITS_ECDSA = math.floor(math.log(FIELD_PRIME, 2))
assert N_ELEMENT_BITS_ECDSA == 251

N_ELEMENT_BITS_HASH = FIELD_PRIME.bit_length()
assert N_ELEMENT_BITS_HASH == 252

# Elliptic curve parameters.
assert 2 ** N_ELEMENT_BITS_ECDSA < EC_ORDER < FIELD_PRIME

SHIFT_POINT = CONSTANT_POINTS[0]
MINUS_SHIFT_POINT = (SHIFT_POINT[0], FIELD_PRIME - SHIFT_POINT[1])
EC_GEN = CONSTANT_POINTS[1]

assert SHIFT_POINT == [
    0x49EE3EBA8C1600700EE1B87EB599F16716B0B1022947733551FDE4050CA6804,
    0x3CA0CFE4B3BC6DDF346D49D06EA0ED34E621062C0E056C1D0405D266E10268A,
]
assert EC_GEN == [
    0x1EF15C18599971B7BECED415A40F0C7DEACFD9B0D1819E03D723D8BC943CFCA,
    0x5668060AA49730B7BE4801DF46EC62DE53ECD11ABE43A32873000C36E8DC1F,
]


def from_bytes(
    value: bytes,
    byte_order = None,
    signed = None,
) -> int:
    """
    Converts the given bytes object (parsed according to the given byte order) to an integer.
    Default byte order is 'big'.
    """
    if byte_order is None:
        byte_order = "big"

    if signed is None:
        signed = False

    return int.from_bytes(value, byteorder=byte_order, signed=signed)

def to_bytes(
    value: int,
    length = None,
    byte_order= None,
    signed = None,
) -> bytes:
    """
    Converts the given integer to a bytes object of given length and byte order.
    The default values are 32B width (which is the hash result width) and 'big', respectively.
    """
    if length is None:
        length = HASH_BYTES

    if byte_order is None:
        byte_order = "big"

    if signed is None:
        signed = False

    return int.to_bytes(value, length=length, byteorder=byte_order, signed=signed)

ECSignature = Tuple[int, int]



# A type that represents a point (x,y) on an elliptic curve.
ECPoint = Tuple[int, int]


def pi_as_string(digits: int) -> str:
    """
    Returns pi as a string of decimal digits without the decimal point ("314...").
    """
    mpmath.mp.dps = digits  # Set number of digits.
    return "3" + str(mpmath.mp.pi)[2:]


def is_quad_residue(n: int, p: int) -> bool:
    """
    Returns True if n is a quadratic residue mod p.
    """
    return sympy.is_quad_residue(n, p)


def sqrt_mod(n: int, p: int) -> int:
    """
    Finds the minimum positive integer m such that (m*m) % p == n
    """
    return min(sympy.sqrt_mod(n, p, all_roots=True))


def div_mod(n: int, m: int, p: int) -> int:
    """
    Finds a nonnegative integer 0 <= x < p such that (m * x) % p == n
    """
    a, b, c = igcdex(m, p)
    assert c == 1
    return (n * a) % p


def ec_add(point1: ECPoint, point2: ECPoint, p: int) -> ECPoint:
    """
    Gets two points on an elliptic curve mod p and returns their sum.
    Assumes the points are given in affine form (x, y) and have different x coordinates.
    """
    assert (point1[0] - point2[0]) % p != 0
    m = div_mod(point1[1] - point2[1], point1[0] - point2[0], p)
    x = (m * m - point1[0] - point2[0]) % p
    y = (m * (point1[0] - x) - point1[1]) % p
    return x, y


def ec_neg(point: ECPoint, p: int) -> ECPoint:
    """
    Given a point (x,y) return (x, -y)
    """
    x, y = point
    return (x, (-y) % p)


def ec_double(point: ECPoint, alpha: int, p: int) -> ECPoint:
    """
    Doubles a point on an elliptic curve with the equation y^2 = x^3 + alpha*x + beta mod p.
    Assumes the point is given in affine form (x, y) and has y != 0.
    """
    assert point[1] % p != 0
    m = div_mod(3 * point[0] * point[0] + alpha, 2 * point[1], p)
    x = (m * m - 2 * point[0]) % p
    y = (m * (point[0] - x) - point[1]) % p
    return x, y


def ec_mult(m: int, point: ECPoint, alpha: int, p: int) -> ECPoint:
    """
    Multiplies by m a point on the elliptic curve with equation y^2 = x^3 + alpha*x + beta mod p.
    Assumes the point is given in affine form (x, y) and that 0 < m < order(point).
    """
    if m == 1:
        return point
    if m % 2 == 0:
        return ec_mult(m // 2, ec_double(point, alpha, p), alpha, p)
    return ec_add(ec_mult(m - 1, point, alpha, p), point, p)



def pedersen(input):
    point = SHIFT_POINT
    for i in range(len(input)):
        x = int(input[i], 16)
        assert 0 <= x < FIELD_PRIME, "Element integer value is out of range"
        for j in range(252):
            pt = CONSTANT_POINTS[2 + i*252 + j]
            assert pt[0] != point[0]
            if x & 1 != 0:
                point = ec_add(point, pt, FIELD_PRIME)
            x = x >> 1
    return hex(point[0])

def hashMsg(
        instructionType,
        vault0,
        vault1,
        amount0,
        amount1,
        nonce,
        expirationTimestamp,
        token0,
        token1OrPubKey,
        condition = None
):
    packed_message = instructionType
    packed_message = (packed_message << 31) + vault0
    packed_message = (packed_message << 31) + vault1
    packed_message = (packed_message << 63) + amount0
    packed_message = (packed_message << 63) + amount1
    packed_message = (packed_message << 31) + nonce
    packed_message = (packed_message << 22) + expirationTimestamp
    msgHash = None
    if condition == None:
        msgHash = pedersen(
            [pedersen([token0, token1OrPubKey]), hex(packed_message)]
        )
    else:
        msgHash = pedersen([
            pedersen([
                pedersen([token0, token1OrPubKey]), condition
            ]), hex(packed_message)
        ])
    return msgHash


def inv_mod_curve_size(x: int) -> int:
    return div_mod(1, x, EC_ORDER)


def generate_k_rfc6979(msg_hash: int, priv_key: int, seed = None) -> int:
    # Pad the message hash, for consistency with the elliptic.js library.
    if 1 <= msg_hash.bit_length() % 8 <= 4 and msg_hash.bit_length() >= 248:
        # Only if we are one-nibble short:
        msg_hash *= 16

    if seed is None:
        extra_entropy = b""
    else:
        extra_entropy = seed.to_bytes(math.ceil(seed.bit_length() / 8), "big")

    return generate_k(
        EC_ORDER,
        priv_key,
        hashlib.sha256,
        msg_hash.to_bytes(math.ceil(msg_hash.bit_length() / 8), "big"),
        extra_entropy=extra_entropy,
    )

def sign(msg_hash: int, priv_key: int, seed = None) -> ECSignature:
    # Note: msg_hash must be smaller than 2**N_ELEMENT_BITS_ECDSA.
    # Message whose hash is >= 2**N_ELEMENT_BITS_ECDSA cannot be signed.
    # This happens with a very small probability.
    assert 0 <= msg_hash < 2**N_ELEMENT_BITS_ECDSA, "Message not signable."

    # Choose a valid k. In our version of ECDSA not every k value is valid,
    # and there is a negligible probability a drawn k cannot be used for signing.
    # This is why we have this loop.
    while True:
        k = generate_k_rfc6979(msg_hash, priv_key, seed)
        # Update seed for next iteration in case the value of k is bad.
        if seed is None:
            seed = 1
        else:
            seed += 1

        # Cannot fail because 0 < k < EC_ORDER and EC_ORDER is prime.
        x = ec_mult(k, EC_GEN, ALPHA, FIELD_PRIME)[0]

        # DIFF: in classic ECDSA, we take int(x) % n.
        r = int(x)
        if not (1 <= r < 2**N_ELEMENT_BITS_ECDSA):
            # Bad value. This fails with negligible probability.
            continue

        if (msg_hash + r * priv_key) % EC_ORDER == 0:
            # Bad value. This fails with negligible probability.
            continue

        w = div_mod(k, msg_hash + r * priv_key, EC_ORDER)
        if not (1 <= w < 2**N_ELEMENT_BITS_ECDSA):
            # Bad value. This fails with negligible probability.
            continue

        s = inv_mod_curve_size(w)
        return r, s


def private_key_to_ec_point_on_stark_curve(priv_key: int) -> ECPoint:
    assert 0 < priv_key < EC_ORDER
    return ec_mult(priv_key, EC_GEN, ALPHA, FIELD_PRIME)


def private_to_stark_key(priv_key: int) -> int:
    return private_key_to_ec_point_on_stark_curve(priv_key)[0]
    