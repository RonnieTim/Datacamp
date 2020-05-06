# Define count_entries()
def count_entries(df, col_name='lang'):
    """Return a dictionary with counts of
    occurrences as value for each key."""
    cols_count = {}
    col = df[col_name]
    for entry in col:
        if entry in cols_count.keys():
            cols_count[entry] += 1
        else:
            cols_count[entry] = 1

    return cols_count
result1 = count_entries(tweets_df,'lang')
result2 = count_entries(tweets_df, 'source')
print(result1)
print(result2)


-----------
# Define count_entries()
def count_entries(df, *args):
    """Return a dictionary with counts of
    occurrences as value for each key."""
    cols_count = {}
    for col_name in args:
        col = df[col_name]
        for entry in col:
            if entry in cols_count.keys():
                cols_count[entry] += 1
            else:
                cols_count[entry] = 1
    return cols_count

-------------------
# Create a list of strings: spells
spells = ["protego", "accio", "expecto patronum", "legilimens"]
shout_spells = map(lambda item: item + '!!!', spells)
shout_spells_list = list(shout_spells)

print(shout_spells_list)

---------------------
# Create a list of strings: fellowship
fellowship = ['frodo', 'samwise', 'merry', 'pippin', 'aragorn', 'boromir', 'legolas', 'gimli', 'gandalf']

result = filter(lambda member: len(member) > 6, fellowship)

result_list = list(result)

print(result_list)

-----------------------

# Import reduce from functools
from functools import reduce

# Create a list of strings: stark
stark = ['robb', 'sansa', 'arya', 'brandon', 'rickon']

# Use reduce() to apply a lambda function over stark: result
result = reduce(lambda item1,item2: item1 + item2, stark)

# Print the result
print(result)


-----------------
# Define shout_echo
def shout_echo(word1, echo=1):
    """Concatenate echo copies of word1 and three
    exclamation marks at the end of the string."""
    echo_word = ""
    shout_words = ""

    try:
        echo_word = word1 * echo
        shout_words = echo_word + "!!!"
    except:
        print("word1 must be a string and echo must be an integer.")

    return shout_words
shout_echo("particle", echo="accelerator")

result1 = count_entries(tweets_df, 'lang')
result2 = count_entries(tweets_df, 'lang', 'source')
print(result1)
print(result2)

-----------------
# Define shout_echo
def shout_echo(word1, echo=1):
    """Concatenate echo copies of word1 and three
    exclamation marks at the end of the string."""
    if echo < 0:
       raise  ValueError('echo must be greater than or equal to 0')

    echo_word = word1 * echo
    shout_word = echo_word + '!!!'
    return shout_word

shout_echo("particle", echo=5)

---------------------
# Select retweets from the Twitter DataFrame: result
result = filter(lambda x: x[0:2]=='RT', tweets_df['text'])
res_list = list(result)
for tweet in res_list:
    print(tweet)

-------------------------


# Define count_entries()
def count_entries(df, col_name='lang'):
    """Return a dictionary with counts of
    occurrences as value for each key."""
    cols_count = {}
    try:
        col = df[col_name]
        for entry in col:

            if entry in cols_count.keys():
                cols_count[entry] += 1

            else:
                cols_count[entry] = 1
        return cols_count

    except:
        print('The DataFrame does not have a ' + col_name + ' column.')


result1 = count_entries(tweets_df, 'lang')

print(result1)


-------------------------


# Define count_entries()
def count_entries(df, col_name='lang'):
    """Return a dictionary with counts of
    occurrences as value for each key."""
    if col_name not in df.columns:
        raise ValueError('The DataFrame does not have a ' + col_name + ' column.')
    cols_count = {}
    col = df[col_name]

    for entry in col:
        if entry in cols_count.keys():
            cols_count[entry] += 1
        else:
            cols_count[entry] = 1

    return cols_count


result1 = count_entries(tweets_df, 'lang')

print(result1)