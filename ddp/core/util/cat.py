# cats = ["charlene", "cheesecake", "kiki"]

# for cat in cats:
#     print cat + " is the best"
#     if cat == "cheesecake":
#         print "we're done!"
#         break


def is_cheesy(cats):
    for cat in cats:
        if cat == "cheesecake":
            return True
    return False

print is_cheesy(["charlene", "kiki", "cheesecake", "ghastly"])



