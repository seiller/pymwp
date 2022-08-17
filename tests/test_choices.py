from pymwp.choice import Choices


def test_choices_can_be_parameterized():
    index, choices = 3, [0, 1, 2, 3]
    inf = {((0, 0), (0, 1)),
           ((0, 0), (1, 1), (3, 2)),
           ((1, 0), (1, 1), (3, 2)),
           ((2, 0), (1, 1), (3, 2)),
           ((3, 0), (1, 1), (3, 2))}
    result = Choices.generate(choices, index, inf)

    assert not result.infinite
    assert len(result.valid) == 4
    assert [[1, 2, 3], [0, 2, 3], [0, 1, 2, 3]] in result.valid  # !(0,0) (1,1)
    assert [[1, 2, 3], [0, 1, 2, 3], [0, 1, 2]] in result.valid  # !(0,0) (3,2)
    assert [[0, 1, 2, 3], [2, 3], [0, 1, 2, 3]] in result.valid  # !(0,1) (1,1)
    assert [[0, 1, 2, 3], [1, 2, 3], [0, 1, 2]] in result.valid  # !(0,1) (3,2)


def test_infinite_eval():
    index, choices = 4, [0, 1, 2]
    infinite = {((0, 3),), ((1, 3),), ((2, 3),)}
    result = Choices.generate(choices, index, infinite)
    assert result.infinite


def test_is_valid_returns_correct_result():
    index, choices = 2, [0, 1, 2]
    infinite = {((0, 1),), ((1, 0), (2, 1))}
    obj = Choices.generate(choices, index, infinite)

    # by (0, 1) not allowed to have 0 at index 1
    assert not obj.is_valid(0, 0)
    assert not obj.is_valid(1, 0)
    assert not obj.is_valid(2, 0)

    # by (1, 0), (2, 1) not allowed to choose 1, 2
    assert not obj.is_valid(1, 2)

    # all other choices are ok
    assert obj.is_valid(0, 1)
    assert obj.is_valid(1, 1)
    assert obj.is_valid(2, 1)
    assert obj.is_valid(0, 2)
    assert obj.is_valid(2, 2)


def test_result_is_minimal():
    # ref: https://github.com/statycc/pymwp/issues/80
    index, choices = 3, [0, 1, 2]
    infinite = {((0, 0),),
                ((1, 0),),
                ((2, 1), (1, 2)),
                ((2, 0), (1, 1), (1, 2))}
    result = Choices.generate(choices, index, infinite)

    assert [[2], [0, 1, 2], [0, 2]] in result.valid
    assert [[2], [0, 1], [0, 2]] not in result.valid
    assert [[2], [0, 2], [0, 2]] not in result.valid
    assert [[2], [0], [0, 1, 2]] in result.valid
