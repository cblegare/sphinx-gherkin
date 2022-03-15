Feature: Some feature
  Lenghty description here

  Including some ref (see :background:`.a simple background`).

  Background: a simple background
    Given the minimalism inside a background

  # Comment above
  # a second line above
  @some_tag
  @issue:1234
  Scenario: Minimalistic
    # Comment within
    # a second line within
    Given some markdown
      """markdown
      Markdown docstring
      """
    And this is duplicated
    And a data table
      | header |
      | one    |
      | two    |
    When the sky is blue
    Then I can hear the light

  Scenario: also minimalistic
    Given the minimalism
    And this is duplicated

  Scenario: Ending with a dot.

  Scenario: duplicated

    Given Something

  Rule: My Rule

    Background:
      Given a rule background step

    Scenario Outline: with examples
      Given the <value> minimalism

      Examples:
        | value |
        | 1     |
        | 2     |

    Scenario: duplicated
